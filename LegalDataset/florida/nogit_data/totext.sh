# nrobot 20 Mar 2023 

# Convert pdf files in docs/ folder to text files in text/ folder 
# If `pdftotext` not installed, use `apt install poppler-utils`
# Run with sh ./totext.sh  | tee -a log.txt

TOTAL=$(ls -U docs | wc -l)
COUNT=0
mkdir text -pv # make folder, ignore error if already exists

cd docs
echo "Current folder: $(pwd)"

for file in *.pdf
do 
    if [ -f "../text/$file.txt" ]; then 
        echo "File exists"
    else 
        pdftotext "$file" "../text/$file.txt"
    fi
    COUNT=$((COUNT+1))
    echo "[ $COUNT / $TOTAL ] --  Processed $file"
done

cd - 
echo "Current folder: $(pwd)"
echo "Done."
