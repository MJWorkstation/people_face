# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
import re
import people_recognition.api as people_recognition
import multiprocessing
import sys
import itertools


def print_result(filename, location):
    top, right, bottom, left = location
    print("{},{},{},{},{}".format(filename, top, right, bottom, left))


def test_image(image_to_check, model, upsample):
    unknown_image = people_recognition.load_image_file(image_to_check)
    people_locations = people_recognition.people_locations(unknown_image, number_of_times_to_upsample=upsample, model=model)

    for people_location in people_locations:
        print_result(image_to_check, people_location)


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def process_images_in_process_pool(images_to_check, number_of_cpus, model, upsample):
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
        itertools.repeat(model),
        itertools.repeat(upsample),
    )

    pool.starmap(test_image, function_parameters)


@click.command()
@click.argument('image_to_check')
@click.option('--cpus', default=1, help='number of CPU cores to use in parallel. -1 means "use all in system"')
@click.option('--model', default="hog", help='Which people detection model to use. Options are "hog" or "cnn".')
@click.option('--upsample', default=0, help='How many times to upsample the image looking for peoples. Higher numbers find smaller peoples.')
def main(image_to_check, cpus, model, upsample):
    if (sys.version_info < (3, 4)) and cpus != 1:
        click.echo("WARNING: Multi-processing support requires Python 3.4 or greater. Falling back to single-threaded processing!")
        cpus = 1

    if os.path.isdir(image_to_check):
        if cpus == 1:
            [test_image(image_file, model, upsample) for image_file in image_files_in_folder(image_to_check)]
        else:
            process_images_in_process_pool(image_files_in_folder(image_to_check), cpus, model, upsample)
    else:
        test_image(image_to_check, model, upsample)


if __name__ == "__main__":
    main()
