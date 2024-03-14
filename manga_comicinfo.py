import os

def count_files(path):
  """Counts image files, tracks chapters, and extracts volume numbers."""
  chapter_number = None
  image_count = 0
  folder_name, volume_number = extract_version(os.path.basename(path))
  for root, _, files in os.walk(path):
    for file in files:
      if not file.startswith('.'):  # Ignore hidden files
        extension = file.split('.')[-1].lower()
        if extension in ['jpg', 'jpeg', 'png']:  # Check for image extensions
          image_count += 1
          c_number = find_number(file)
          if c_number and c_number != chapter_number:
            chapter_number = c_number
            yield f"Bookmark=\"Chapter {chapter_number}\" Image=\"{image_count - 1}\""
          else:
            yield f"Image=\"{image_count - 1}\""

def find_number(filename):
  """Extracts the chapter number (3/4 digits) following either " - c" or " - d" from the filename."""
  identifiers = ["c", "d"]
  for identifier in identifiers:
    identifier_index = filename.rfind(f" - {identifier}")
    if identifier == "c":
        if identifier_index != -1 and len(filename) >= identifier_index + 7:
            try:
                return int(filename[identifier_index + 4:identifier_index + 7])
            except ValueError:
                pass  # Ignore non-numeric characters after identifier
    elif identifier == "d":
        if identifier_index != -1 and len(filename) >= identifier_index + 8:
            try:
                return int(filename[identifier_index + 4:identifier_index + 8])
            except ValueError:
                pass  # Ignore non-numeric characters after identifier
  return None

def extract_version(folder_name):
  """Extracts volume number (v01) from folder name."""
  v_index = folder_name.rfind('v')
  if v_index != -1 and v_index + 1 < len(folder_name):
    try:
      volume_number = int(folder_name[v_index + 1:])
      return folder_name[:v_index].rstrip(), volume_number  # Remove trailing spaces
    except ValueError:
      pass  # Ignore non-numeric characters after 'v'
  return folder_name.rstrip(), None  # Remove trailing spaces even without volume number

def create_comicinfo(path):
  """Creates a text file with folder name, chapter bookmarks, numbered images, and volume number (if applicable)."""
  folder_name, volume_number = extract_version(os.path.basename(path))
  with open('ComicInfo.xml', 'w') as f:
    f.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n')
    f.write('<ComicInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">\n')
    f.write('  <Series>' + folder_name + '</Series>\n')  # No spaces, so no need for rstrip() here
    if volume_number:
      f.write('  <Volume>' + str(volume_number) + '</Volume>\n')  # Omit the "v"
    f.write('  <Pages>\n')
    for line in count_files(path):
      f.write('    <Page ' + line + ' />\n')
    f.write('  </Pages>\n')
    f.write('</ComicInfo>')

# Get current working directory
current_path = os.getcwd()

# Create ComicInfo.xml
create_comicinfo(current_path)

print("Created ComicInfo.xml")
