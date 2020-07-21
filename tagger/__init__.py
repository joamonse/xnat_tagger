import argparse
import csv

from pkg_resources import resource_filename

from tagger.app import App


def main():
    description = 'XNAT Image tagger tool'
    parser = argparse.ArgumentParser(description=description,
                                     epilog='--from-file and --from-xnat are mutually exclusive')

    parser.add_argument('-o',
                        help='File Name where result is stored.',
                        metavar="FILENAME",
                        dest="output",
                        required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-x', '--from-xnat', nargs=2, dest='xnat_url_project', help='Url and project of xnat.',
                       metavar=("XNAT_URL", "PROJECT"))
    group.add_argument('-f', '--from-file',  dest='input_filename', help='Filename of previous execution.',
                       metavar='FILENAME')

    parser.add_argument('-n', '--buffer-size',  dest='buffer_size', type=int, default=10, metavar='NUMBER')
    parser.add_argument('-u', '--xnat-user',  dest='xnat_user', metavar='USER', required=True)
    parser.add_argument('-p', '--xnat-password', dest='xnat_password', default="", metavar='PASSWORD')

    args = parser.parse_args()

    options_file = resource_filename(__name__, 'resources/default_choices.json')

    if not args.xnat_url_project:
        xnat_url = None
        xnat_proj = None

    else:
        xnat_url = args.xnat_url_project[0]
        xnat_proj = args.xnat_url_project[1]

    app = App(args.buffer_size, options_file, args.input_filename, args.output, xnat_url, xnat_proj, args.xnat_user,
              args.xnat_password)
    with app:
        app.run()


if __name__ == "__main__":
    main()
