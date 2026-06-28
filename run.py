"""
Entry point for the CAPTCHA project.

Usage:
  python run.py train          # Train the AI solver
  python run.py api            # Start the web API (http://localhost:8000)
  python run.py demo           # Generate and display a sample CAPTCHA
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_train():
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    from solver.train import train
    train()


def cmd_api():
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080)


def cmd_demo():
    import io
    from generator.captcha_gen import generate_captcha
    img, text = generate_captcha()
    path = "demo_captcha.png"
    img.save(path)
    print(f"CAPTCHA saved to {path}")
    print(f"Text: {text}")
    try:
        os.startfile(path)
    except Exception:
        pass


COMMANDS = {
    "train": cmd_train,
    "api": cmd_api,
    "demo": cmd_demo,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
