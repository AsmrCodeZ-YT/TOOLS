@echo off
REM Check if youtube-comment-downloader is installed
pip show youtube-comment-downloader >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo youtube-comment-downloader is not installed. Installing now...
    pip install youtube-comment-downloader
) ELSE (
    echo youtube-comment-downloader is already installed.
)

REM Ask the user for the YouTube video link
set /p video_url=Please enter the YouTube video URL: 

REM Run the command to download comments
youtube-comment-downloader --url %video_url% --output comments.json

echo Comments have been successfully saved.
pause
