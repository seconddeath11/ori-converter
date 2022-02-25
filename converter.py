import json
import os
from PIL import Image
import pandas as pd
import xml.etree.ElementTree as Et
import shutil


def saver(func):
    """
    Decorate saving functions, catch file errors.
    """
    def wrapper(*args):
        print("Saving ...", end="")
        try:
            func(*args)
            print("Done")
        except OSError as e:
            print("Couldn't save: ", e)
        except Exception as e:
            print("Something went wrong:", e)
            exit()

    return wrapper


class Format:
    """
    Base class for all formats.
    """
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.image_path = os.path.join(self.input_folder, "images")
        self.image_folder = os.path.split(self.image_path)[-1]
        self.check_paths()

    def get_boxes_by_image(self, image):
        """
        Get boxes connected with the image.
        :param image: filename of the image to get boxes from
        :return: generator
        """
        pass

    @staticmethod
    def add_obj_to_annotation(annotation, box):
        """
        Add object to annotation in PascalVOC format.
        :param annotation: prepared annotation to add objects to
        :param box: object to add to annotation
        """
        obj = Et.SubElement(annotation, "object")
        Et.SubElement(obj, "name").text = box["class"]
        Et.SubElement(obj, "pose").text = "Unspecified"
        Et.SubElement(obj, "truncated").text = "0"
        Et.SubElement(obj, "difficult").text = "0"

        bndbox = Et.SubElement(obj, "bndbox")
        Et.SubElement(bndbox, "xmin").text = str(box["xmin"])
        Et.SubElement(bndbox, "ymin").text = str(box["ymin"])
        Et.SubElement(bndbox, "xmax").text = str(box["xmax"])
        Et.SubElement(bndbox, "ymax").text = str(box["ymax"])

    @staticmethod
    def create_annotation(image, root):
        """
        Create annotation object in PascalVOC format.
        :param image: dict with image properties
        :param root: parent for annotation
        :return: annotation in PascalVOC format
        """
        annotation = Et.SubElement(root, "annotation")

        Et.SubElement(annotation, "folder").text = image["folder"]
        Et.SubElement(annotation, "filename").text = image["filename"]
        Et.SubElement(annotation, "path").text = image["path"]

        source = Et.SubElement(annotation, "source")
        Et.SubElement(source, "database").text = "ORI_Markup"

        size = Et.SubElement(annotation, "size")
        Et.SubElement(size, "width").text = str(image["width"])
        Et.SubElement(size, "height").text = str(image["height"])
        Et.SubElement(size, "depth").text = "3"

        Et.SubElement(annotation, "segmented").text = "0"
        return annotation

    def get_images_info(self):
        """
        Iterate over each image in directory and get its info.
        :return: generator over images
        """
        for image_name in sorted(os.listdir(self.image_path)):
            image = self.image_info(image_name)
            if image is not None:
                yield image

    def image_info(self, image_name):
        """
        Get image's properties.
        :param image_name: filename of the image
        :return: image properties in a dict | None
        """
        image = {"filename": image_name}
        try:
            with Image.open(os.path.join(self.image_path, image_name)) as img:
                image["width"], image["height"] = img.size
        except IOError:
            print("Found wrong file extension: not an image")
            return None
        return image

    @saver
    def save_to_json(self, data, file):
        """
        Save data to json file.
        :param data: information to save
        :param file: filename to save the data to
        """
        with open(file, 'w') as f:
            json.dump(data, f)

    @saver
    def save(self, data, file):
        """
        Save data to the file.
        :param data: information to save
        :param file: filename to save data to
        """
        with open(file, 'w') as f:
            f.write(data)

    @saver
    def save_to_csv(self, path, data, columns):
        """
        Save data to csv file.
        :param path: path to the file to save to
        :param data: information to save to the file
        :param columns: list of data columns
        """
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(path, index=False)

    def copy_images(self):
        """
        Copy image folder to the specified output folder.
        """
        shutil.copytree(self.image_path, os.path.join(self.output_folder, self.image_folder))

    def check_paths(self):
        """
        Check if paths are proper.
        """
        print("Opening input folder...", end=" ")
        self.error_handler(os.path.exists(self.input_folder), "Done", "Can not find input folder. "
                                                                      "Exiting", exit)
        print("Opening folder with images...", end=" ")
        self.error_handler(os.path.exists(self.image_path), "Done",
                           "Can not find images folder. Exiting", exit)
        self.error_handler(os.path.exists(self.output_folder), "Opening output folder", "Creating output folder",
                           os.mkdir, self.output_folder)
        self.error_handler(not os.path.exists(os.path.join(self.output_folder, "images")),
                           "Creating output folder for images",
                           "Folder for images already exists in output. Exiting", exit)

    @staticmethod
    def error_handler(statement, true_log_text, false_log_text, func=None, *args):
        """
        Check the statement and print result, if False execute function.
        :param statement: the clause to check
        :param true_log_text: text to print if statement is true
        :param false_log_text: text to print if statement is false
        :param func: function to execute if the statement is false
        :param args: arguments for func
        """
        if statement:
            print(true_log_text)
        else:
            print(false_log_text)
            func(*args)


class Int(Format):
    """
    Internal format of data storage. Child class of the Format class.
    """
    def __init__(self, input_folder, output_folder):
        super().__init__(input_folder, output_folder)
        self.markup_path = os.path.join(input_folder, "markup")
        self.markup_csv = os.path.join(output_folder, "markup.csv")

    def get_boxes_by_image(self, image):
        json_name = os.path.join(self.markup_path, image.split(".")[0] + ".json")
        try:
            with open(json_name, "r") as f:
                photo_info = json.load(f)
                for box in photo_info:
                    yield box
        except OSError:
            print("Problem occurred with file ", json_name)
            exit()

    def to_int_csv(self):
        """
        Convert Internal format to InternalCSV and save to the output folder.
        """
        data = []
        images = self.get_images_info()
        for image in images:
            print(f"Converting image {image['filename']}")
            boxes = self.get_boxes_by_image(image["filename"])
            for box in boxes:
                data.append(self.line_to_csv(image, box))
        columns = ["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"]
        self.save_to_csv(self.markup_csv, data, columns)
        self.copy_images()

    def line_to_csv(self, image, box):
        """
        Map info to InternalCSV format columns.
        :param image: dict of image properties
        :param box: dict of box's properties
        :return: dict of mapped info about the box
        """
        return {"filename": os.path.join(self.image_folder, image["filename"]), "width": image["width"],
                "height": image["height"],
                "class": box["label"], "xmin": box["x"], "ymin": box["y"],
                "xmax": box["x1"], "ymax": box["y1"]}


class IntCSV(Format):
    """
    InternalCSV format of data storage. Child class of the Format class.
    """
    def __init__(self, input_folder, output_folder):
        super().__init__(input_folder, output_folder)
        self.markup_csv = os.path.join(input_folder, "markup.csv")
        self.markup_path = os.path.join(output_folder, "markup")
        try:
            self.data = pd.read_csv(self.markup_csv)
        except IOError:
            print("Problem occurred with file ", self.markup_csv)
            exit()

    def get_boxes_by_image(self, image):
        for idx, row in self.data[self.data["filename"] == (os.path.join(self.image_folder, image))].iterrows():
            yield row

    def to_pascal_voc(self):
        """
        Convert InternalCSV format to PascalVOC and save data to the output folder.
        """
        root = Et.Element("root")
        images = self.get_images_info()
        for image in images:
            print(f"Converting image {image['filename']}")
            boxes = self.get_boxes_by_image(image["filename"])
            ann = self.create_annotation(self.line_to_pascal(image), root)
            for row in boxes:
                self.add_obj_to_annotation(ann, row)
        Et.indent(root, space="\t")
        tree = Et.tostring(root, encoding="unicode")
        self.save(tree, os.path.join(self.output_folder, "markup.xml"))
        self.copy_images()

    def to_int(self):
        """
        Convert InternalCSV format to Internal and save data to the output folder.
        """
        labels = set()
        images = self.get_images_info()
        if not os.path.exists(self.markup_path):
            os.mkdir(self.markup_path)
        for image in images:
            box_list = []
            print(f"Converting image {image['filename']}")
            boxes = self.get_boxes_by_image(image["filename"])
            for row in boxes:
                labels.add(row["class"])
                box_list.append(self.line_to_int(row))
            self.save_to_json(box_list,
                              os.path.join(self.output_folder, "markup", image["filename"].split(".")[0] + ".json"))
        self.save_to_json({"labels": list(labels)}, os.path.join(self.output_folder, "meta.json"))
        self.copy_images()

    @staticmethod
    def line_to_int(row):
        """
        Map InternalCSV row to match Internal columns.
        :param row: box properties
        :return: dict with mapped info of the box
        """
        return {"x": row["xmin"], "y": row["ymin"], "x1": row["xmax"], "y1": row["ymax"], "label": row["class"]}

    def line_to_pascal(self, image):
        """
        Map InternalCSV row to match PascalVOC labels.
        :param image: dict with image properties
        :return: dict with mapped info of the image
        """
        return {"folder": self.image_folder, "filename": image["filename"],
                "path": os.path.abspath(os.path.join(self.output_folder, "images", image["filename"])),
                "width": image["width"], "height": image["height"]}


class PascalVOC(Format):
    """
    PascalVOC format of data storage. Child class of the Format class.
    """
    def __init__(self, input_folder, output_folder):
        super().__init__(input_folder, output_folder)
        self.markup_xml = os.path.join(input_folder, "markup.xml")
        self.markup_csv = os.path.join(output_folder, "markup.csv")
        try:
            self.tree = Et.parse(self.markup_xml)
        except Et.ParseError:
            print("Problem occurred with file ", self.markup_xml)
            exit()

    def get_boxes_by_image(self, image):
        ann = self.tree.find(".//*[filename='%s']" % (image["filename"]))
        for obj in ann.findall("object"):
            yield obj

    def to_int_csv(self):
        """
        Convert PascalVOC format to InternalCSV and save data to the output folder.
        """
        data = []
        images = self.get_images_info()
        for image in images:
            print(f"Converting image {image['filename']}")
            boxes = self.get_boxes_by_image(image)
            for box in boxes:
                data.append(self.line_to_csv(image, box))
        columns = ["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"]
        self.save_to_csv(self.markup_csv, data, columns)
        self.copy_images()

    def line_to_csv(self, image, box):
        """
        Map PascalVOC info to match InternalCSV format.
        :param image: dict with image properties
        :param box: element of PascalVOC tree with properties of the box
        :return: dict with mapped info of the image and the box
        """
        return {"filename": os.path.join(self.image_folder, image["filename"]), "width": image["width"],
                "height": image["height"], "class": box.find("name").text, "xmin": box.find("bndbox/xmin").text,
                "ymin": box.find("bndbox/ymin").text, "xmax": box.find("bndbox/xmax").text,
                "ymax": box.find("bndbox/ymax").text}


if __name__ == '__main__':
    # Get all env variables
    in_folder = os.getenv("input_folder")
    out_folder = os.getenv("output_folder")
    in_format = os.getenv("input_format")
    out_format = os.getenv("output_format")

    # Dict with all available input formats
    formats = {
        "int": Int,
        "int_csv": IntCSV,
        "pascal_voc": PascalVOC
    }
    inp = formats.get(in_format)

    if inp is None:
        print("The input format is not supported. Available formats are: ", *formats)
        exit()
    if in_folder is None:
        print("Output folder is not specified")
        exit()
    if out_folder is None:
        print("Output folder is not specified")
        exit()
    if out_format is None:
        print("Output format is not specified")
        exit()

    out = "to_" + out_format

    # Check if input format class has the function to convert to output format
    op = getattr(inp, out, None)
    if callable(op):
        converter = inp(in_folder, out_folder)
        op(converter)
    else:
        print("This conversion is not supported")
