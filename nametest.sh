
declare -a arr=("playing in the band" "not fade away" "me and my uncle" "sugar magnolia" "the other one" "i know you rider" "china cat sunflower" "truckin" "jack straw" "good lovin")

for i in "${arr[@]}"
do
   python3 nametest2.py "$i"
done