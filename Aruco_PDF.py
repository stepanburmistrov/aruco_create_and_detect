import cv2
import numpy as np
import os
from fpdf import FPDF



def createArucoMarkerWithBorder(markerSize, markerId, imgSize):
    """
    Создает Aruco маркер с белой рамкой.
    
    :param markerSize: Размер маркера (например, 4x4, 5x5).
    :param markerId: ID маркера.
    :param imgSize: Разрешение изображения маркера.
    :return: Сохраняет маркер в файл.
    """
    # Создаем словарь Aruco маркеров нужного размера
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250 if markerSize == 4 else cv2.aruco.DICT_5X5_250)

    # Генерируем маркер
    markerImage = np.zeros((imgSize, imgSize), dtype=np.uint8)
    cv2.aruco.drawMarker(arucoDict, markerId, imgSize, markerImage, 1)

    # Рассчитываем размер нового изображения с рамкой
    borderSize = imgSize // (markerSize + 2)
    newSize = imgSize + borderSize * 2 + 2

    # Создаем новое изображение с белой рамкой
    newImage = np.ones((newSize, newSize), dtype=np.uint8) * 255
    newImage[borderSize + 1:-borderSize - 1, borderSize + 1:-borderSize - 1] = markerImage
    
    # Добавляем пунктирную линию на крайних пикселях рамки
    for i in range(0, newSize, 4):
        newImage[i:i+2, 0] = 0
        newImage[i:i+2, -1] = 0
        newImage[0, i:i+2] = 0
        newImage[-1, i:i+2] = 0

    # Добавляем текст с ID маркера
    text = f"{markerId}"
    targetTextHeight = imgSize * 0.07  # 7% от высоты изображения
    fontScale = 0.1  # Начальный масштаб шрифта
    thickness = 1 * int(imgSize / 500)
    textSize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale, thickness)[0]

    # Подбираем масштаб шрифта, чтобы высота текста была приблизительно 7% от imgSize
    while textSize[1] < targetTextHeight:
        fontScale += 0.1
        textSize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale, thickness)[0]

    textX = newSize - textSize[0] - int(imgSize * 0.02)  # от правого края
    textY = newSize - int(imgSize * 0.02)  # от нижнего края
    cv2.putText(newImage, text, (textX, textY), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 0), thickness)

    # Сохраняем маркер в файл
    #cv2.imwrite(f"aruco_marker_{markerId}_with_border.png", newImage)
    return newImage
    


def createArucoMarkersPDF(markerList, mmSize):
    """
    Создает PDF файл с Aruco маркерами, учитывая поля в 15 мм.
    
    :param markerList: Список маркеров в формате (размер маркера, ID, размер изображения).
    :param mmSize: Размер маркера в миллиметрах.
    """
    # Проверяем и создаем папку для маркеров
    folderName = "ArucoMarkers"
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    # Создаем маркеры и сохраняем их в папку
    for markerSize, markerId, imgSize in markerList:
        markerImage = createArucoMarkerWithBorder(markerSize, markerId, imgSize)
        cv2.imwrite(f"{folderName}/aruco_marker_{markerId}_with_border.png", markerImage)

    # Создаем PDF
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    margin = 15  # Поля в мм
    current_x, current_y = margin, margin
    page_width, page_height = 210, 297  # Размеры страницы A4 в мм

    for markerSize, markerId, imgSize in markerList:
        filePath = f"{folderName}/aruco_marker_{markerId}_with_border.png"
        if os.path.exists(filePath):
            if current_x + mmSize > page_width - margin:
                current_x = margin
                current_y += mmSize
            if current_y + mmSize > page_height - margin:
                pdf.add_page()
                current_x, current_y = margin, margin
            pdf.image(filePath, x=current_x, y=current_y, w=mmSize, h=mmSize)
            current_x += mmSize
    # Сохраняем PDF
    pdf.output(f"{folderName}/ArucoMarkers.pdf")

# Пример использования функции
marker_list = [(4, 2, 1000), (4, 1, 1000)]*15
createArucoMarkersPDF(marker_list, 70)  # Создает PDF с маркерами размером 50 мм
