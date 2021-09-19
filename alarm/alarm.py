import argparse
import os
from pathlib import Path
import random
import sys
import time

from dotenv import load_dotenv
from playsound import playsound


class AlarmFileException(Exception):
    """To be used in case of an invalid alarm file"""


def countdown_and_play_alarm(
    seconds: int, alarm_file: str, display_timer: bool = False
) -> None:
    while seconds:
        mins, secs = divmod(seconds, 60)
        if display_timer:
            print(f"{mins:02}:{secs:02}", end="\r")
        time.sleep(1)
        seconds -= 1

    if display_timer:
        print("00:00", end="\r")
    playsound(alarm_file)


def get_args():
    parser = argparse.ArgumentParser("Play an alarm after N minutes")

    duration_group = parser.add_mutually_exclusive_group(required=True)
    duration_group.add_argument(
        "-s", "--seconds", type=int, help="Number of seconds before playing alarm"
    )
    duration_group.add_argument(
        "-m", "--minutes", type=int, help="Number of minutes before playing alarm"
    )

    run_mode_group = parser.add_mutually_exclusive_group()
    run_mode_group.add_argument(
        "-b",
        "--background",
        action="store_true",
        default=False,
        help="Run timer in the background",
    )
    run_mode_group.add_argument(
        "-d",
        "--display_timer",
        action="store_true",
        default=False,
        help="Show timer in console",
    )

    alarm_file_group = parser.add_mutually_exclusive_group()
    alarm_file_group.add_argument(
        "-l", "--song_library", help="Take a random song from a song library directory"
    )
    alarm_file_group.add_argument(
        "-f", "--file", help="File path to song to play as alarm"
    )
    return parser.parse_args()


def _get_file(args) -> str:
    if args.song_library:
        music_files = list(Path(args.song_library).rglob("*.mp[34]"))
        if not music_files:
            raise AlarmFileException(f"No music files found in {args.song_library}")
        return str(random.choice(music_files))
    elif args.file:
        return args.file
    else:
        load_dotenv()
        return os.environ["ALARM_MUSIC_FILE"]


def _validate_file(file: str) -> None:
    if not Path(file).exists():
        raise AlarmFileException(f"{file} does not exist")
    allowed_extensions = ("mp3", "mp4")
    if not Path(file).suffix.endswith(allowed_extensions):
        raise AlarmFileException(
            f"{file} is not supported ({', '.join(allowed_extensions)} files are)"
        )


def get_alarm_file(args) -> str:
    file = _get_file(args)
    _validate_file(file)
    return file


def main(args=None):
    if args is None:
        args = get_args()

    minutes = int(args.seconds) / 60 if args.seconds else int(args.minutes)
    if args.background:
        print(f"Playing alarm in {minutes} minute{'' if minutes == 1 else 's'}")

        package = __package__
        module = Path(sys.argv[0]).stem

        os.system(f"python -m {package}.{module} -m {minutes} &")
    else:
        seconds = minutes * 60
        try:
            alarm_file = get_alarm_file(args)
            countdown_and_play_alarm(
                seconds, alarm_file, display_timer=args.display_timer
            )
            sys.exit(0)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
