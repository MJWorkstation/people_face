# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
import re
import people_recognition.api as people_recognition
import multiprocessing
import itertools
import sys
import PIL.Image
import numpy as np


def scan_known_people(known_people_folder):
    known_names = []
    known_people_encodings = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = people_recognition.load_image_file(file)
        encodings = people_recognition.people_encodings(img)

        if len(encodings) > 1:
            click.echo("WARNING: More than one people found in {}. Only considering the first people.".format(file))

        if len(encodings) == 0:
            click.echo("WARNING: No peoples found in {}. Ignoring file.".format(file))
        else:
            known_names.append(basename)
            known_people_encodings.append(encodings[0])

    return known_names, known_people_encodings


def print_result(filename, name, distance, show_distance=False):
    if show_distance:
        print("{},{},{}".format(filename, name, distance))
    else:
        print("{},{}".format(filename, name))


def test_image(image_to_check, known_names, known_people_encodings, tolerance=0.6, show_distance=False):
    unknown_image = people_recognition.load_image_file(image_to_check)

    if max(unknown_image.shape) > 1600:
        pil_img = PIL.Image.fromarray(unknown_image)
        pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
        unknown_image = np.array(pil_img)

    unknown_encodings = people_recognition.people_encodings(unknown_image)

    for unknown_encoding in unknown_encodings:
        distances = people_recognition.people_distance(known_people_encodings, unknown_encoding)
        result = list(distances <= tolerance)

        if True in result:
            [print_result(image_to_check, name, distance, show_distance) for is_match, name, distance in zip(result, known_names, distances) if is_match]
        else:
            print_result(image_to_check, "unknown_person", None, show_distance)

    if not unknown_encodings:
        print_result(image_to_check, "no_persons_found", None, show_distance)


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def process_images_in_process_pool(images_to_check, known_names, known_people_encodings, number_of_cpus, tolerance, show_distance):
    if number_of_cpus == -1:
        processes = None
    else:
        processes = number_of_cpus

    context = multiprocessing
    if "forkserver" in multiprocessing.get_all_start_methods():
        context = multiprocessing.get_context("forkserver")

    pool = context.Pool(processes=processes)

    function_parameters = zip(
        images_to_check,
        itertools.repeat(known_names),
        itertools.repeat(known_people_encodings),
        itertools.repeat(tolerance),
        itertools.repeat(show_distance)
    )

    pool.starmap(test_image, function_parameters)


@click.command()
@click.argument('known_people_folder')
@click.argument('image_to_check')
@click.option('--cpus', default=1, help='number of CPU cores to use in parallel (can speed up processing lots of images). -1 means "use all in system"')
@click.option('--tolerance', default=0.6, help='Tolerance for people comparisons. Default is 0.6. Lower this if you get multiple matches for the same person.')
@click.option('--show-distance', default=False, type=bool, help='Output people distance. Useful for tweaking tolerance setting.')
def main(known_people_folder, image_to_check, cpus, tolerance, show_distance):
    known_names, known_people_encodings = scan_known_people(known_people_folder)

    if (sys.version_info < (3, 4)) and cpus != 1:
        click.echo("WARNING: Multi-processing support requires Python 3.4 or greater. Falling back to single-threaded processing!")
        cpus = 1

    if os.path.isdir(image_to_check):
        if cpus == 1:
            [test_image(image_file, known_names, known_people_encodings, tolerance, show_distance) for image_file in image_files_in_folder(image_to_check)]
        else:
            process_images_in_process_pool(image_files_in_folder(image_to_check), known_names, known_people_encodings, cpus, tolerance, show_distance)
    else:
        test_image(image_to_check, known_names, known_people_encodings, tolerance, show_distance)


if __name__ == "__main__":
    main()
