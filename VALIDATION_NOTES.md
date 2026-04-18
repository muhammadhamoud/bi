# Validation Notes

What was validated in the build environment:
- The full project source was generated and packaged.
- Python syntax was checked with `python -m compileall` after generation and patching.

What was not executed in the build environment:
- `pip install -r requirements.txt`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver`

Reason:
- The container used for assembly did not have Django installed and did not have network access to download packages, so runtime validation could not be completed here.

Expected local validation flow:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_all_demo
python manage.py runserver
```
