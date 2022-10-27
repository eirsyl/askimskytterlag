import os
import shutil
import sys
from datetime import date
from logging import getLogger
from pathlib import Path
from chardet.universaldetector import UniversalDetector
from pydantic import BaseModel

logger = getLogger()

RESULT_INFO_FILE = "info.json"
IGNORE_FILES = [".DS_Store"]
CHECK_ENCODING = [".htm", ".html", ".css", ".js"]


class ResultInfo(BaseModel):
    """
    Metadata for each 'stevne' in the results folder.
    """

    name: str
    start_date: date
    end_date: date


class Result(BaseModel):
    info: ResultInfo
    path: Path

    def name(self) -> str:
        return f"{self.info.name} {self.info.start_date.year}"


def ensure_directory(*, path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def empty_directory(*, path: Path) -> None:
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def tidy_out_folder(*, path: Path) -> None:
    """
    Remove unnecessary files and fix encoding.
    """
    detector = UniversalDetector()

    for folder, _, files in os.walk(path):
        # Skip files in the root folder, they are managed
        # by this script.
        if folder == str(path):
            continue

        for file in files:
            file_path = Path(folder) / file

            # Delete ignored files
            if file in IGNORE_FILES:
                file_path.unlink(missing_ok=True)
                continue

            # Check and rewrite file in UTF-8 if needed
            if file.endswith(tuple(CHECK_ENCODING)):
                # Get encoding
                detector.reset()

                for line in open(file_path, "rb"):
                    detector.feed(line)
                    if detector.done:
                        break

                detector.close()
                encoding = detector.result["encoding"]

                # Rewrite file with UTF-8 encoding
                with open(file_path, mode="r", encoding=encoding) as f:
                    file_content = f.read()

                with open(file_path, mode="w", encoding="utf-8") as f:
                    f.write(file_content)


def build_results(*, results_path: Path) -> list[Result]:
    results: list[Result] = []

    for path in results_path.iterdir():
        if path.is_dir():
            info_file = path / RESULT_INFO_FILE

            # Make sure the info file exists.
            if not info_file.is_file():
                logger.warning(
                    "Skipping folder %s, no result info file found.",
                    path,
                )
                continue

            result_info = ResultInfo.parse_file(info_file)

            results.append(Result(info=result_info, path=path))

    return results


def build_index_page(*, results: list[Result], out_path: Path) -> None:
    def sort_func(result: Result) -> tuple[date, str]:
        return result.info.start_date, result.info.name

    sorted_results = sorted(results, key=sort_func, reverse=True)

    result_list = "".join(
        [
            f'<li><a href="{result.path.name}">{result.name()}</a></li>'
            for result in sorted_results
        ]
    )

    index_page = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Askim Skytterlag</title>
  </head>
  <body>
    <main>
        <h1>Askim Skytterlag</h1>

        <ul>
            {result_list}
        </ul>

        <br/>
        <p>Source code at <a
          href="https://github.com/eirsyl/askimskytterlag"
        >GitHub</a>, made by Eirik Martiniussen Sylliaas.</p>
    </main>
  </body>
</html>
"""

    index_file_path = out_path / "index.html"

    # Write to index.html
    index_file_path.write_text(index_page, encoding="utf-8")


def maybe_build_redirect_page(results_ouput_path: Path) -> None:
    index_page = results_ouput_path / "index.html"

    other_root_files = ["index.htm", "index.pdf", "StartFrame.htm"]

    if not index_page.exists():
        other_root = [
            file for file in other_root_files if (results_ouput_path / file).exists()
        ]

        if not other_root:
            raise RuntimeError(
                "No other root file was found in %s",
                results_ouput_path,
            )

        result_index = other_root[0]

        redirect = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Askim Skytterlag - Redirecting to {result_index}</title>
    <meta http-equiv="refresh" content="0; URL={result_index}">
    <link rel="canonical" href="{result_index}">
  </head>
  <body>
    <main>
        <p>Redirecting...</p>
    </main>
  </body>
</html>
"""

        index_file_path = results_ouput_path / "index.html"
        index_file_path.write_text(redirect, encoding="utf-8")


def copy_results_files(*, results: list[Result], out_path: Path) -> None:
    def ignore_filter(_: str, names: list[str]) -> list[str]:
        ignores: list[str] = []

        for name in names:
            if RESULT_INFO_FILE in name:
                ignores.append(name)

        return ignores

    for result in results:
        results_ouput_path = out_path / result.path.name

        shutil.copytree(
            result.path,
            results_ouput_path,
            symlinks=False,
            ignore=ignore_filter,
        )

        maybe_build_redirect_page(results_ouput_path)


def main() -> int:
    BASE_PATH = (Path(__file__).parent).resolve()

    RESULTS_PATH = BASE_PATH / "results"
    OUT_PATH = BASE_PATH / "out"

    # Make sure the output directory exists.
    ensure_directory(path=OUT_PATH)

    # Delete old data in the output directory
    empty_directory(path=OUT_PATH)

    # Retrieve results from the results directory
    results = build_results(results_path=RESULTS_PATH)

    # Build the index page
    build_index_page(results=results, out_path=OUT_PATH)

    # Copy results files
    copy_results_files(results=results, out_path=OUT_PATH)

    # Prepare files in the results folder
    tidy_out_folder(path=OUT_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())
