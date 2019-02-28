// image gallery
// init the state from the input
$(".image-checkbox").each(function () {
  count = false;
  if ($(this).find('input[type="checkbox"]').first().attr("checked") && (count == false)) {
    $(this).addClass('image-checkbox-checked');
  }
  else {
    $(this).removeClass('image-checkbox-checked');
    count = true;
  }
});

// sync the state to the input
$(".image-checkbox").on("click", function (e) {
  $(this).toggleClass('image-checkbox-checked');
  var $checkbox = $(this).find('input[type="checkbox"]');
  $checkbox.prop("checked",!$checkbox.prop("checked"))

  e.preventDefault();
});

/*
var socket = io('http://127.0.0.1:5000');
var t1_name, t1_num, t2_name, t2_num


socket.on('connect', function(data) {
  socket.emit('join', 'perks');
});

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1);
    if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
  }
  return "";
}

socket.on(--PERKS_HEADER.TEAMS--, function(data) {
  dictionary = JSON.parse(data)
  if (getCookie('alliance') == 'gold') {
      t1_name = JSON.parse(match_info).g1_name
      t1_num = JSON.parse(match_info).g1_num
      t2_name = JSON.parse(match_info).g2_name
      t2_num = JSON.parse(match_info).g2_num
  } else if (getCookie('alliance') == 'blue') {
      t1_name = JSON.parse(match_info).b1_name
      t1_num = JSON.parse(match_info).b1_num
      t2_name = JSON.parse(match_info).b2_name
      t2_num = JSON.parse(match_info).b2_num
  }
  setTeams()
})

function setTeams() {
    $("#team-1-number").val(t1_num);
    $("#team-1-name").val(t1_name);
    $("#team-2-number").val(t2_num);
    $("#team-2-name").val(t2_name);
}

function blueClick() {
    //TODO: $("blue element") set css
    //TODO: $("gold element") remove css
    document.cookie = "alliance=blue"
}

function goldClick() {
    //TODO: $("gold element") set css
    //TODO: $("blue element") remove css
    document.cookie = "alliance=gold"
}

//onclick
function submitPerks() {
    team_color = getCookie('alliance')
    //TODO: Gather list of selected perks
    //TODO: data = {'alliance' : team_color. 'perk-1' : '' ...}
    //TODO: socket.emit('ui-to-server-selected-perks', JSON.stringify(data))
}*/
