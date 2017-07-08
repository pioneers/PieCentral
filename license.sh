for f in **/*.py; do
    if (grep License $f);then
        echo "Skipped $f"
    else
        echo "Added $f"
        cat header.txt $f > $f.new
        mv $f.new $f
    fi
done
