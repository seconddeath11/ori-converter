#!/bin/bash

function help {
  echo
  echo "Usage: bash start.sh MANDATORY [OPTIONAL]"
  echo
  echo "ARGUMENTS:"
  echo
  echo "MANDATORY:"
  echo "  --in-dir:            Absolute path to directory with initial data"
  echo "  --out-dir:           Absolute path to directory for converted data"
  echo "  --in-format          Initial data's format"
  echo "  --out-format         Desired format"
  echo "  -i,  --image         Image to run"
  echo "OPTIONAL:"
  echo "  -n,  --name          Name for the container"
  echo "  -rm, --rm-container  Remove container after execution"
  echo "  -h,  --help          Prints this help"
  echo
  echo "Usage example:"
  echo "bash start.sh --in-dir \"/home/diana/data\" --out-dir \"/home/diana/data2\" --in-format \"int_csv\" --out-format \"pascal_voc\" -i converter -rm \"True\""
}

remove_cont="True"
cont_name="converter"

while [ -n "$1" ]
do
    case "$1" in
      --in-dir) input_folder="$2" ;;
      --out-dir) output_folder="$2" ;;
      --in-format) input_format="$2" ;;
      --out-format) output_format="$2" ;;
      -i  | -image) image_name="$2" ;;
      -n  | -name) cont_name="$2" ;;
      -rm | --rm-container) remove_cont="$2" ;;
      -h  | --help) help
        exit 0 ;;
      *) echo "$1 is not an option"
        exit 1 ;;
    esac

    case $2 in
    -*) echo "Option $1 needs a valid argument"
    exit 1
    ;;
    esac
    shift
shift
done

if [ -z $input_folder ] || [ -z $output_folder ] || [ -z $input_format ] || [ -z $output_format ] || [ -z $image_name ]; then
    echo "One of the required arguments is empty. Use --help to see instructions"
    exit 1
fi

mkdir -p "$output_folder"
chown $(id -u):$(id -g) "$output_folder"

sudo docker run --user $(id -u):$(id -g) -e input_folder="$input_folder" -e output_folder="$output_folder" -e input_format="$input_format" \
                -e output_format="$output_format" -v $input_folder:$input_folder -v $output_folder:$output_folder --name "$cont_name" "$image_name"
if [ $remove_cont == "True" ]; then
    sudo docker rm -v "$cont_name" > /dev/null
fi