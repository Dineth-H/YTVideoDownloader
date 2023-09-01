import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pytube import YouTube
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser

# Function to update the link preview
def update_link_preview(event=None):
    video_url = url_entry.get()
    try:
        yt = YouTube(video_url)
        title_label.config(text=f"Title: {yt.title}")
        author_label.config(text=f"Author: {yt.author}")
        
        # Convert video duration to a user-friendly format (hours:minutes:seconds)
        duration = yt.length
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}"
        
        views_label.config(text=duration_str)
        status_label.config(text="Link preview updated successfully!")

        # Clear and update quality options
        quality_values = [stream.resolution for stream in yt.streams.filter(progressive=True)]
        quality_combo['values'] = quality_values
        quality_combo.current(0)

        # Load and display the video thumbnail
        thumbnail_url = yt.thumbnail_url
        response = requests.get(thumbnail_url)
        thumbnail_img = Image.open(BytesIO(response.content))
        thumbnail_img = thumbnail_img.resize((160, 90))  # Resize the thumbnail
        thumbnail_photo = ImageTk.PhotoImage(thumbnail_img)
        thumbnail_label.config(image=thumbnail_photo)
        thumbnail_label.image = thumbnail_photo

        # Store the YouTube video URL for later use
        thumbnail_label.video_url = video_url

        # Update file size label when a new quality is selected
        def update_file_size(event=None):
            selected_quality = quality_combo.get()
            selected_stream = yt.streams.filter(progressive=True, resolution=selected_quality).first()
            file_size = selected_stream.filesize / (1024 * 1024)  # Convert to MB
            file_size_str = f"File Size: {file_size:.2f} MB"
            file_size_label.config(text=file_size_str)

        quality_combo.bind("<<ComboboxSelected>>", update_file_size)
        update_file_size()  # Initial update

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 410:
            status_label.config(text="Video not found. It may have been removed.")
        else:
            status_label.config(text=f"HTTP Error: {http_err}")
    except Exception as e:
        title_label.config(text="Title: ")
        author_label.config(text="Author: ")
        views_label.config(text="Duration: ")
        file_size_label.config(text="File Size: ")
        status_label.config(text=f"An error occurred: {str(e)}")
        thumbnail_label.config(image=None)  # Clear the thumbnail
        thumbnail_label.video_url = ""

# Function to open the video in the default web browser
def open_video(event):
    if hasattr(thumbnail_label, 'video_url') and thumbnail_label.video_url:
        webbrowser.open(thumbnail_label.video_url)

# Function to set the download path
def set_download_path():
    download_dir = filedialog.askdirectory()
    if download_dir:
        download_path_entry.delete(0, tk.END)
        download_path_entry.insert(0, download_dir)

# Function to download the video with audio
def download_video():
    video_url = url_entry.get()
    download_dir = download_path_entry.get()
    try:
        yt = YouTube(video_url)
        selected_quality = quality_combo.get()
        selected_stream = yt.streams.filter(progressive=True, resolution=selected_quality).first()
        file_size_label.config(text=f"File Size: {selected_stream.filesize / (1024 * 1024):.2f} MB")
        selected_stream.download(output_path=download_dir)  # Specify the download directory
        status_label.config(text="Download completed successfully!")
    except Exception as e:
        status_label.config(text=f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader by DinethH")
root.geometry("600x550")  # Set the initial window size in pixels

# Load the background GIF as an animated image
background_gif_url = "https://media.giphy.com/media/ySloPYiroerB3QgcYc/giphy.gif"
response = requests.get(background_gif_url)
background_gif = Image.open(BytesIO(response.content))
background_gif = ImageTk.PhotoImage(background_gif)

# Create a label to display the animated background GIF
background_label = tk.Label(root, image=background_gif)
background_label.place(relwidth=1, relheight=1)  # Cover the entire window

# Create a frame for the main content with a transparent background
main_frame = tk.Frame(root, bg="#000", bd=0, relief="flat")
main_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

# Create a label with a transparent background
url_label = tk.Label(main_frame, text="Enter YouTube URL:", bg="#000", fg="white")
url_label.pack()

# Create an entry field
url_entry = tk.Entry(main_frame, width=40, bg="#222", fg="white")
url_entry.pack()

# Bind the event handler to automatically update the link preview when text is inserted
url_entry.bind("<KeyRelease>", update_link_preview)

# Create link preview labels with transparent background
title_label = tk.Label(main_frame, text="Title: ", bg="#000", fg="white")
title_label.pack()
author_label = tk.Label(main_frame, text="Author: ", bg="#000", fg="white")
author_label.pack()
views_label = tk.Label(main_frame, text="Duration: ", bg="#000", fg="white")
views_label.pack()

# Create a quality selection combobox
quality_label = tk.Label(main_frame, text="Select Quality:", bg="#000", fg="white")
quality_label.pack()
quality_combo = ttk.Combobox(main_frame, values=[], state="readonly", background="#222", foreground="white")
quality_combo.pack()

# Create a label for file size
file_size_label = tk.Label(main_frame, text="File Size: ", bg="#000", fg="white")
file_size_label.pack()

# Create an image preview label
thumbnail_label = tk.Label(main_frame, bg="#000")
thumbnail_label.pack()

# Bind the event handler to open the video when the user clicks on the thumbnail
thumbnail_label.bind("<Button-1>", open_video)

# Create a download path label and entry
download_path_label = tk.Label(main_frame, text="Download Path:", bg="#000", fg="white")
download_path_label.pack()
download_path_entry = tk.Entry(main_frame, width=40, bg="#222", fg="white")
download_path_entry.pack()

# Create a download path button with right-click context menu (copy-paste)
download_path_button = tk.Button(main_frame, text="Choose Path", command=set_download_path, bg="#D32F2F", fg="white")
download_path_button.pack()

# Create a download button
download_button = tk.Button(main_frame, text="Download", command=download_video, bg="#D32F2F", fg="white")
download_button.pack(pady=10)  # Move the download button down

# Create a status label with a transparent background
status_label = tk.Label(main_frame, text="", bg="#000", fg="green")
status_label.pack()

# Create a creator label with a transparent background
creator_label = tk.Label(main_frame, text="Created by DinethH using Python 3 - 2023", bg="#000", fg="white")
creator_label.pack(side="bottom")

# Allow copy-paste functionality for the download path entry
download_path_entry.bind("<Control-c>", lambda e: download_path_entry.event_generate("<<Copy>>"))
download_path_entry.bind("<Control-x>", lambda e: download_path_entry.event_generate("<<Cut>>"))
download_path_entry.bind("<Control-v>", lambda e: download_path_entry.event_generate("<<Paste>>"))

# Enable scrolling for the download path entry
download_path_scroll = tk.Scrollbar(download_path_entry, orient="horizontal", command=download_path_entry.xview)
download_path_entry.configure(xscrollcommand=download_path_scroll.set)

# Start the GUI event loop
root.mainloop()
