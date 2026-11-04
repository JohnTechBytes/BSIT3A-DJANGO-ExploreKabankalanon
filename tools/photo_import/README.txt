EXPLORE KABANKALAN - BULK PHOTO IMPORT

1. Put this importer in a photo_import folder in your project folder, next to
   manage.py, and create a photo_import\images subfolder.
2. Put image files in photo_import\images. Name each image with its place ID
   only, keeping its real extension. Examples: 7638.png or 7639.jpg.
   Use one .jpg, .jpeg, .png, or .webp file per ID; maximum 20 MB per file.
   Turn on "File name extensions" in Windows File Explorer if needed.
3. Back up the database and media folder. Start XAMPP MySQL. In PowerShell,
   open the project folder containing manage.py and run the dry run:
   .\.venv\Scripts\python.exe .\photo_import\import_photos
4. Read every ID and title shown and personally check each image against its
   place. An ID is a database match, not proof that the image is authentic.
   Fix any errors. Run the dry run again after changing any file.
5. Only after reviewing the full list, import the images:
   .\.venv\Scripts\python.exe .\photo_import\import_photos --apply

The importer does not create places, publish places, replace existing covers,
or overwrite existing attribution fields. It stops the whole batch on a
problem. It uses a direct database update of cover_image and therefore bypasses
the admin form's attribution/permission validation. Photographer, source and
license are left blank where they were blank; unknown rights are not claimed.
Being publicly visible is not proof an image is free to use. Verify permission
and credit requirements before publishing. Image files are not stripped of
metadata, so remove any sensitive metadata before placing them in the folder.
If the script reports an existing photo or attribution, stop and review that
record separately. A failed batch rolls back database changes and attempts to
remove files created by that batch; keep your backup and read error messages.
After a successful import, move imported originals out of the images folder
before the next batch, or the importer will stop on the existing covers.

To replace an existing local cover, the separate replace_cover helper requires a
place ID, matching image filename, and exact place name. It previews by default,
retains the original media file, and refuses existing rights metadata or an
external cover URL. Use --apply only after reviewing the target and image.
For example:
 .\.venv\Scripts\python.exe .\photo_import\replace_cover 7638 7638.png --expected-name '7-Eleven - Guanzon Street'
