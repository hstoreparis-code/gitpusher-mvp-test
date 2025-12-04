import subprocess

from utils.mailer import send_alert


def run_qa():
    p = subprocess.run(
        ["python3", "scripts/qa_run.py"],
        capture_output=True,
        text=True,
    )
    return p.returncode, p.stdout + "\n" + p.stderr


def main():
    code, logs = run_qa()
    if code != 0:
        send_alert("GitPusher QA FAILED", logs)


if __name__ == "__main__":
    main()
