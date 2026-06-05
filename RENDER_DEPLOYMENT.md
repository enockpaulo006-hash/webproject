# Render Deployment Notes

This project is prepared for Render as a Django web service.

## Render settings

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`
- Health check path: `/healthz/`

## Required environment variables

Set these in Render if you are not using `render.yaml`:

```txt
SECRET_KEY=<generate a secure value>
DEBUG=False
ALLOWED_HOSTS=<your-service-name>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-service-name>.onrender.com
DATABASE_URL=<Render Postgres internal connection string>
```

Optional tuning values:

```txt
DB_CONN_MAX_AGE=600
PRODUCTS_PER_PAGE=12
PRODUCT_IMAGE_MAX_WIDTH=1200
PRODUCT_IMAGE_MAX_HEIGHT=1200
PRODUCT_IMAGE_QUALITY=82
EMAIL_TIMEOUT=5
```

## Uploaded product images

New uploads are compressed automatically by the product form.

To check existing images before launch:

```bash
python manage.py optimize_product_images --dry-run
```

To optimize existing images:

```bash
python manage.py optimize_product_images
```

Render's normal filesystem is temporary. For permanent user uploads, use a persistent disk on a paid Render service or cloud storage such as S3/Cloudinary.

Do not commit local uploaded media, browser cache folders, SQLite databases, or Python bytecode. They make Render deploys larger and can accidentally publish local-only data.

## Email OTP

The app now handles SMTP failures gracefully. Render Free services can have SMTP limits, so use a supported email provider/API or a paid service if Gmail SMTP does not send.

## Free plan cold starts

Render Free services can sleep after inactivity. Code changes cannot remove that delay; use a paid Render plan or an external monitor if startup delay is unacceptable.
