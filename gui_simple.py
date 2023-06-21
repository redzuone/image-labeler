from main import process_single_file, process_images_in_folder, extract_text, load_model, save_image, show_image, ocr
import PySimpleGUI as sg
from paddleocr import draw_ocr
from PIL import Image

show_image_flag = False
rename_file_flag = False
def main():
    global show_image_flag, rename_file_flag
    sg.theme('DarkAmber')
    layout = [[sg.Button('Process a file')],
                [sg.Button('Process a folder')],
                [sg.Text('Path: ', key='path')],
                [sg.Checkbox('Show image result (single image)', enable_events=True, key='show_image_event')],
                [sg.Checkbox('Rename file directly', enable_events=True, key='rename_file_event')],
                [sg.Text('Status: '), sg.Text('Ready', key='status')],
                [sg.Col([[sg.T('Results')]], scrollable=True, key='-COL-', s=(1280,720))],]
    window = sg.Window('Image Labeler', layout, size=(1280, 720))
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'show_image_event':
            show_image_flag = window['show_image_event'].get()
        elif event == 'rename_file_event':
            rename_file_flag = window['rename_file_event'].get()
        elif event == 'Process a file':
            img_path = sg.popup_get_file('Pick file')
            if not img_path:
                continue
            else:
                window['path'].update(img_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: process_single_file(img_path), 'single_file_done')
        elif event == 'single_file_done':
            text, result = values[event]
            window['status'].update('Done')
            save_image_box_gui(img_path, result)
            #window.extend_layout(window['-COL-'], [[sg.T('A New Input Line'), sg.I(key=f'-IN-')]])
            window.extend_layout(window['-COL-'], [[sg.Image(filename='tmp.png', size=(None, 300))],
                                                   [sg.T(text, size=(300, None))],
                                                   [sg.Button('Accept', key='save'), sg.Button('Reject', key='reject')]])
            #window.extend_layout(window['-COL-'], [[sg.Image(filename='tmp.png', size=(None, 300))]])
            window.visibility_changed()
            window['-COL-'].contents_changed()
            if show_image_flag == True:
                img_path = window['path'].get()
                show_image(img_path, result)
        elif event == 'Process a folder':
            folder_path = sg.popup_get_folder('Pick folder')
            if not folder_path:
                continue
            else:
                window['path'].update(folder_path)
                window['status'].update('Processing...')
                window.perform_long_operation(lambda: process_images_in_folder(folder_path), 'folder_done')
        elif event == 'folder_done':
            window['status'].update('Done, files are saved in output folder')
            #text, result = values[event]
            #save_image_box_gui(img_path, result)
            #window.extend_layout(window['-COL-'], [[sg.Image(filename='tmp.png', size=(None, 300)), sg.T(text, size=(300, None))]])
            #window.visibility_changed()
            #window['-COL-'].contents_changed()

def save_image_box_gui(img_path, result):
    """
    Save temp image with bounding boxes
    """
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='Roboto-Regular.ttf')
    im_show = Image.fromarray(im_show)

    # Calculate new width based on new height and original aspect ratio
    new_height = 300
    aspect_ratio = im_show.width / im_show.height
    new_width = int(aspect_ratio * new_height)
    
    # Resize image while maintaining aspect ratio
    im_show = im_show.resize((new_width, new_height))

    im_show.save('tmp.png')

if __name__ == '__main__':
    main()