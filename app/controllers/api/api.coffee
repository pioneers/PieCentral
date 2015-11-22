express = require('express')
router = express.Router()
fs = require('fs')
require('connect-busboy')

router.post '/editor/save', (req, res) ->
  filename = req.body.filename
  code = req.body.code
  fs.writeFile('../runtime/student_code/' + filename, code, (err) ->
    if err?
      res.status(500).end()
    res.status(200).end()
  )

router.post '/editor/create', (req, res) ->
  filename = req.body.filename
  fs.writeFile('../runtime/student_code/' + filename, '', (err) ->
    if err?
      res.status(500).end()
    res.status(200).end()
  )

router.delete '/editor/delete/:filename', (req, res) ->
  filename = req.params.filename
  if filename != 'student_code.py'
    fs.unlinkSync('../runtime/student_code/' + filename)
    res.status(200).end()
  else
    res.status(401).end()

router.get '/editor/load', (req, res) ->
  filename = req.query.filename
  fs.readFile('../runtime/student_code/' + filename, (err, data) ->
    if err?
      console.log err
      res.status(500).end()
    res.status(200).send(data)
  )

router.get '/editor/list', (req, res) ->
  filenames = fs.readdirSync('../runtime/student_code/')
  res.status(200).send({filenames: filenames})

router.get '/editor/download', (req, res) ->
  res.download('../runtime/student_code/' + req.query.filename)

router.post '/editor/upload', (req, res) ->
  if req.busboy
    req.busboy.on('file', (fieldname, file, filename, encoding, mimetype) ->
      file.pipe(fs.createWriteStream('../runtime/student_code/' + filename))
    )
    req.busboy.on('finish', () ->
      res.status(200).end()
    )
    req.pipe(req.busboy)

module.exports = router
