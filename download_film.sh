#!/bin/bash

# Базовая URL-часть
BASE_URL="https://nl06.cdnsqu.com/s/FHsKo_7p7g6XUUbsHV-rYCrEFBQUFBRXFsTlVFUlV0Q0ZndUFoa3dBQg.YaZjvNeLyNrccVlp83BcEjG104QMJDWq4jUv4Q/Interny_HD.2010"

# Каталог для сохранения видео
OUTPUT_DIR="./videos"

# Убедитесь, что каталог для видео существует
mkdir -p "$OUTPUT_DIR"

# Цикл от 1 до 60
for i in $(seq -w 1 60); do
  # Формируем имя файла
  FILENAME="s01e${i}_480.mp4"
  
  # Полный URL
  FULL_URL="${BASE_URL}/${FILENAME}"

  # Скачиваем файл
  echo "Скачиваю ${FULL_URL}..."
  curl -o "$OUTPUT_DIR/$FILENAME" "$FULL_URL"

  # Проверяем успешность загрузки
  if [[ $? -eq 0 ]]; then
    echo "Файл ${FILENAME} успешно скачан."
  else
    echo "Ошибка при скачивании ${FILENAME}. Пропуск."
  fi

done

echo "Все операции завершены."
