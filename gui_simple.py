from main import process_single_file, process_images_in_folder, extract_text, load_model, save_image, show_image, ocr
import PySimpleGUI as sg

show_image_flag = False
def main():
    global show_image_flag
    sg.theme('DarkAmber')
    layout = [[sg.Button('Process a file')],
                [sg.Button('Process a folder')],
                [sg.Text('Path: ', key='path')],
                [sg.Checkbox('Show image result(single image)', enable_events=True, key='show_image_event')],
                [sg.Text('Status: '), sg.Text('Ready', key='status')]]
    window = sg.Window('Image Labeler', layout, size=(640, 480))
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'show_image_event':
            show_image_flag = window['show_image_event'].get()
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
            window['status'].update('Text extracted: ' + text)
            
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

if __name__ == '__main__':
    main()