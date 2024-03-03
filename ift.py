import sys
import os
import subprocess
from PIL import Image, ImageFilter
from stegano import lsb

def install_requirements():
    print("[*] Installing required libraries...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        print("[*] Libraries installed successfully.")
    except subprocess.CalledProcessError:
        print("[!] Error installing required libraries. Please install them manually using 'pip install -r requirements.txt'.")
        sys.exit(1)

def install_exiftool():
    print("[*] ExifTool is required for extracting metadata.")
    choice = input("[*] Do you want to install ExifTool? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            subprocess.run(['sudo', 'apt', 'install', 'exiftool'], check=True)
            print("[*] ExifTool installed successfully.")
        except subprocess.CalledProcessError:
            print("[!] Error installing ExifTool. Please install it manually using 'sudo apt install exiftool'.")
            sys.exit(1)
    else:
        print("[!] ExifTool is required for metadata extraction. Exiting...")
        sys.exit(1)

def check_stegano(image_path, passphrase=None):
    try:
        if passphrase:
            secret_data = lsb.reveal(image_path, passphrase=passphrase)
        else:
            secret_data = lsb.reveal(image_path)
            
        if secret_data:
            print("[*] Hidden data found in the image:")
            print(secret_data)
        else:
            print("[*] No hidden data found in the image.")
    except Exception as e:
        print("[!] Error detecting hidden data:", str(e))

try:
    from PIL import Image, ImageFilter
except ImportError:
    print("[!] PIL (Python Imaging Library) is not available.")
    install_requirements()

try:
    subprocess.run(['exiftool', sys.argv[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except FileNotFoundError:
    install_exiftool()

class ImageForensicsToolkit:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)

    def show_ascii_banner(self):
        print(r"""
 ___                              _____                        _          
|_ _|_ __ ___   __ _  __ _  ___  |  ___|__  _ __ ___ _ __  ___(_) ___ ___ 
 | || '_ ` _ \ / _` |/ _` |/ _ \ | |_ / _ \| '__/ _ \ '_ \/ __| |/ __/ __|
 | || | | | | | (_| | (_| |  __/ |  _| (_) | | |  __/ | | \__ \ | (__\__ \
|___|_| |_| |_|\__,_|\__, |\___| |_|  \___/|_|  \___|_| |_|___/_|\___|___/
 _____           _ _ |___/                                                
|_   _|__   ___ | | | _(_) |_                                              
  | |/ _ \ / _ \| | |/ / | __|                                             
  | | (_) | (_) | |   <| | |_                                              
  |_|\___/ \___/|_|_|\_\_|\__| 
                     @abhinav066                                            
        """)

    def extract_metadata(self):
        try:
            exiftool_output = subprocess.run(['exiftool', self.image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("[*] Extracted Metadata:")
            print(exiftool_output.stdout.decode())
        except subprocess.CalledProcessError as e:
            print("[!] Error extracting metadata:", e.stderr.decode())

    def analyze_image(self):
        self.show_ascii_banner()
        print("[*] Analyzing image:", self.image_path)
        self.extract_metadata()
        print("[*] Image Size:", self.image.size)
        print("[*] Image Mode:", self.image.mode)
        print("[*] Color Channels (R, G, B):", self.image.split())
        check_stegano(self.image_path)

    def rotate_image(self, degrees):
        self.image = self.image.rotate(degrees)

    def apply_filter(self, filter_name):
        if filter_name.lower() == 'grayscale':
            self.image = self.image.convert('L')
        elif filter_name.lower() == 'blur':
            self.image = self.image.filter(ImageFilter.BLUR)
        # Add more filters as needed

    def save_image(self, output_path):
        self.image.save(output_path)

    def crack_steghide(self, wordlist_path):
        with open(wordlist_path, 'r') as f:
            for line in f:
                passphrase = line.strip()
                print(f"[*] Trying passphrase: {passphrase}")
                try:
                    output = subprocess.check_output(['steghide', 'extract', '-sf', self.image_path, '-p', passphrase])
                    output_str = output.decode()
                    if 'could not extract any data' not in output_str.lower():
                        print("[*] Passphrase cracked:", passphrase)
                        print("[*] Hidden data extracted successfully:")
                        print(output_str)
                        return  # Stop after finding the correct passphrase
                except subprocess.CalledProcessError:
                    pass  # Incorrect passphrase, continue with the next one
        print("[*] Passphrase not found in the wordlist.")

def main():
    if len(sys.argv) != 2:
        print("[!] Usage: python ift.py <image_path>")
        return

    image_path = sys.argv[1]
    if not os.path.isfile(image_path):
        print("[!] Error: Image file not found.")
        return

    toolkit = ImageForensicsToolkit(image_path)
    toolkit.analyze_image()

    # Example of rotating the image by 90 degrees
    toolkit.rotate_image(90)

    # Example of applying a grayscale filter
    toolkit.apply_filter('grayscale')

    # Example of saving the manipulated image
    output_path = "output.jpg"
    toolkit.save_image(output_path)
    print(f"[*] Manipulated image saved to: {output_path}")

    # Crack steghide
    wordlist_path = "wordlist.txt"  # Provide the path to your wordlist
    toolkit.crack_steghide(wordlist_path)

if __name__ == "__main__":
    main()

