# Image Labeler

Renames pictures based on the text in them using PaddleOCR. 

# Usage
Install [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/quickstart_en.md).    
Command line: Run `main.py` directly or with arguments
```
--filename=FILE     Process a single image
--directory=DIR     Process multiples images in a folder
--rename            Rename file instead of copying the file with a new name  
```

GUI: Run `gui_simple.py` 
The program creates copies the image file with its new name by default.

# To-do
- [x] Image preview in GUI
- [ ] Ability to accept/reject filename
- [x] Rename existing files instead of copying
- [ ] Object/content recognition (maybe)
- [ ] Add more comments
- [ ] Remove common/unnecessary text from new filename/pick most useful text
- [ ] Clean code 🤓

# Libraries used
- PaddleOCR
- PySimpleGUI

![Demo](./demo.gif)