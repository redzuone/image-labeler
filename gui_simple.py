from main import process_single_file, process_images_in_folder, show_image
import PySimpleGUI as sg
import logging

def main():
    show_image_flag = rename_file_flag = False
    sg.theme('DarkAmber')
    layout = [[sg.Button('Process a file')],
                [sg.Button('Process a folder')],
                [sg.Text('Path: ', key='path')],
                [sg.Checkbox('Show image result using matplotlib (single image)', enable_events=True, key='show_image_event')],
                [sg.Checkbox('Rename file instead of copying', enable_events=True, key='rename_file_event')],
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
                window.perform_long_operation(lambda: process_single_file(img_path, rename_file_flag), 'single_file_done')
        elif event == 'single_file_done':
            text, result = values[event]
            window['status'].update('Done')
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


if __name__ == '__main__':
    main()