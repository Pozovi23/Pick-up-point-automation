#include <Wire.h>
#include <queue>
#include <string>
#include <WiFi.h> 
#include <WebServer.h>     // Подключаем библиотеку для создания веб-сервера

uint8_t data[6] = {0};
uint8_t prev_data[6] = {0};
uint8_t occupied[6] = {0};
int BOX = 0;
int LAST = 0; 
#define SLAVE1_ADDR 0x10

// ********************************************************
// *                      API                             *
// ********************************************************

// Настройки точки доступа
// const char* ssid = "ESP32_AP";       // Имя точки доступа
// const char* password = "123456789";   // Пароль для точки доступа
const char* ssid = "domru_2";       // Имя точки доступа
const char* password = "220006005034";   // Пароль для точки доступа

WebServer server; // Создаем объект веб-сервера

// Переменные для хранения данных
int box_id = -1; // Переменная для первой страницы, возвращает одно число
int receivedNumber = 0; // Переменная для хранения числа, полученного от клиента

// Функция для обработки запроса на третью страницу
void handleSetNumber() {
  // Проверяем, был ли передан параметр "number" в запросе
  if (server.hasArg("number")) {
    // Преобразуем значение параметра "number" в целое число и сохраняем в receivedNumber
    receivedNumber = server.arg("number").toInt();
    
    // Отправляем ответ с кодом 200 (OK) и текстом, подтверждающим получение числа
    server.send(200, "text/plain", "Received number: " + String(receivedNumber));
  } else {
    // Если параметр "number" не был передан, отправляем ответ с кодом 400 (Bad Request)
    server.send(400, "text/plain", "Missing number parameter");
  }
}

// Функция для обработки запроса на первую страницу
void handleNumber() {
  // Отправляем ответ с кодом 200 (OK) и текстом, содержащим значение number1
  server.send(200, "text/plain", String(box_id));
}


// ********************************************************
// *                     SETUP                            *
// ********************************************************

void setup() {
  //Wire.begin(); // Инициализация I2C на пинах GPIO 22 (SCL), GPIO 21 (SDA)
  Wire.begin(25, 26); // Инициализация I2C на пинах 25 (SDA) и 26 (SCL)
   // Настраиваем ESP32 как точку доступа
  // WiFi.softAP(ssid, password); // Создаем точку доступа с заданным SSID и паролем
  // подключение к WiFi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED){
    delay(500);

  }

  // Настройка маршрутов для обработки запросов
  server.on("/number", handleNumber); // Обработка запроса на /number
  server.on("/setNumber", handleSetNumber); // Обработка запроса на /setNumber?number=1
  // Запускаем веб-сервер
  server.begin();

  Wire.setClock(100000); //100кГц
  Serial.begin(115200);
   // Отключаем вывод
  // Serial.end();
  writeToSlaves(SLAVE1_ADDR, 0x00);
  writeToSlaves(SLAVE1_ADDR+1, 0x00);
  writeToSlaves(SLAVE1_ADDR+2, 0x00);
  writeToSlaves(SLAVE1_ADDR+3, 0x00);

}

// ********************************************************
// *                      BOX                             *
// ********************************************************

struct Box {
    int id; // Идентификатор коробки
    int position; // Позиция на датчике

    Box(int id) : id(id), position(0) {}
};

class BoxTracker {
  public:
      void add_box(int id) {
          Box newBox(id);
          boxQueue.push(newBox);
      }

      void update_position(int newPosition) {
          std::queue<Box> tempQueue;

          while (!boxQueue.empty()) {
              Box currentBox = boxQueue.front();
              boxQueue.pop();

              if (currentBox.position == newPosition-1) {
                currentBox.position = newPosition;
              }

              if (newPosition == 4 && currentBox.position == 2){
                currentBox.position = newPosition;
              }
              tempQueue.push(currentBox);
          }

          boxQueue = tempQueue; // Обновляем оригинальную очередь
      }

      int check_position() {
          std::queue<Box> tempQueue;

          while (!boxQueue.empty()) {
              Box currentBox = boxQueue.front();
              boxQueue.pop();
              if (currentBox.position == 0 || currentBox.position == 1) {
                return 1;
              }
              tempQueue.push(currentBox);
          }

          boxQueue = tempQueue; // Обновляем оригинальную очередь
          return 0;
      }

      int remove_box() {
          if (!boxQueue.empty()) {
              int removedId = boxQueue.front().id;
              boxQueue.pop();
              return removedId;
          }
        return -1;
      }

      std::queue<Box> get_queue() {
          return boxQueue;
      }

      Box get_first_box() {
          if (!boxQueue.empty()) {
              return boxQueue.front(); // Возвращаем первый элемент
          }
      }
  
  private:
    std::queue<Box> boxQueue;
};

// запись в устройство
void writeToSlaves(uint8_t slaveAddr, uint8_t dataToSend) {
      Wire.beginTransmission(slaveAddr); // Начинаем передачу
      Wire.write(dataToSend); // Записываем байт
      Wire.endTransmission(); // Завершаем передачу
    }



// ********************************************************
// *                    PLATFORMS                         *
// ********************************************************
class Platform{
  public:
    void start(){
      writeToSlaves(SLAVE1_ADDR, 0x01);
      writeToSlaves(SLAVE1_ADDR+1, 0x01);
      // writeToSlaves(SLAVE1_ADDR+2, 0x01);
      writeToSlaves(SLAVE1_ADDR+3, 0x01);
    }

    void stop(){
      writeToSlaves(SLAVE1_ADDR, 0x00);
      writeToSlaves(SLAVE1_ADDR+1, 0x00);
      // writeToSlaves(SLAVE1_ADDR+2, 0x00);
      writeToSlaves(SLAVE1_ADDR+3, 0x00);
    }
};

class Tern{
  public:
    void start(){
      writeToSlaves(SLAVE1_ADDR+3, 0x02);
      writeToSlaves(SLAVE1_ADDR+4, 0x01);
      writeToSlaves(SLAVE1_ADDR+5, 0x01);
    }

    void stop(){
      for (uint8_t i=4; i<6; i++){
        writeToSlaves(SLAVE1_ADDR + i, 0x00);
      }
    }

    void lift_stop(){
      writeToSlaves(SLAVE1_ADDR + 3, 0x01);
    }
};

// чтение с даттчиков
uint8_t readFromSlaves(uint8_t slaveAddr) {
  uint8_t data;
  Wire.requestFrom(slaveAddr, 1); // Запрашиваем 1 байт

  if (Wire.available()) {
    data = Wire.read(); // Читаем байт
    return data;
  } else {
    return 0;
  }

}

BoxTracker tracker;
Platform platform;
Tern tern;
int check=0;


// ********************************************************
// *                  MAIN LOOP                           *
// ********************************************************
void loop() {
  for (uint8_t i=0; i<6; i++){
    if ((SLAVE1_ADDR + i) != 0x13){
      data[i] = readFromSlaves((SLAVE1_ADDR + i)) & 0x01;
    }
  }

  if (prev_data[5] != data[5]){
    if (data[5] == 0x01){
      tern.stop();
      tracker.update_position(5);
      box_id = tracker.remove_box();
      occupied[5] = 1;
    }
  }

  
  if (prev_data[0] != data[0]){
      if (data[0] == 0x01){
        tracker.add_box(BOX);
        tracker.update_position(0);
        BOX++;
        if (!occupied[1]){
          platform.start();
        }

      }
      else{
        if (BOX != 0){
          tracker.update_position(1);
        }
      }
  }
  

  if (prev_data[1] != data[1]){
    if (data[1] != 0x01){
      if (!occupied[2]){
        tracker.update_position(2);
      }
      else{
        platform.stop();
        occupied[1] = 1;
      }
    }
  }

  if (prev_data[2] != data[2]){
      if (data[2] == 0x01){
        if (!occupied[4]){
          platform.stop();
          tern.start();
          delay(3000);
          tern.lift_stop();
        }
        else if (occupied[4] && !occupied[2]){
          platform.stop();
          occupied[2] = 1;

        }
      }
  }
  

  check = 0;
  if (prev_data[4] != data[4]){
      if (data[4] == 0x01){
        tracker.update_position(4);
        check = tracker.check_position();
        if (data[4] == 0x01 && check == 1){
          platform.start();
        }
        if (occupied[5]){
          tern.stop();
          // tracker.update_position(4);
          occupied[4] = 1;
        }
      }
      
  }

  for (int i=0; i<6; i++){
    if (prev_data[i] != data[i]){
      prev_data[i] = data[i];
    }
  }

  server.handleClient(); // Обработка входящих клиентов
  if (receivedNumber == 1){
    for (int i=0; i<6; i++){
      occupied[i] = 0;
      prev_data[i] = 0;
    }
    box_id = -1;
    delay(3000);
  }
}


// ********************************************************
// *                      TESTS                           *
// ********************************************************


// ********************************************************
// *                    BOX TESTS                         *
// ********************************************************
void testBoxTracker() {
  Serial.println("Running BoxTracker tests...");
  
  BoxTracker tracker;
  int testPassed = 0;
  int testFailed = 0;

  // Тест 1: Добавление коробки
  tracker.add_box(1);
  if (tracker.get_queue().size() == 1) {
    Serial.println("Test 1 Passed: Box added successfully");
    testPassed++;
  } else {
    Serial.println("Test 1 Failed: Box not added");
    testFailed++;
  }

  // Тест 2: Обновление позиции
  tracker.update_position(1);
  if (tracker.get_first_box().position == 1) {
    Serial.println("Test 2 Passed: Position updated");
    testPassed++;
  } else {
    Serial.println("Test 2 Failed: Position not updated");
    testFailed++;
  }

  // Тест 3: Проверка позиции
  int check = tracker.check_position();
  if (check == 1) {
    Serial.println("Test 3 Passed: Position check correct");
    testPassed++;
  } else {
    Serial.println("Test 3 Failed: Position check incorrect");
    testFailed++;
  }

  // Тест 4: Удаление коробки
  int removedId = tracker.remove_box();
  if (removedId == 1 && tracker.get_queue().empty()) {
    Serial.println("Test 4 Passed: Box removed");
    testPassed++;
  } else {
    Serial.println("Test 4 Failed: Box not removed");
    testFailed++;
  }

  Serial.printf("BoxTracker Tests: %d Passed, %d Failed\n\n", testPassed, testFailed);
}


// ********************************************************
// *                  PLATFORM TESTS                      *
// ********************************************************
void testPlatform() {
  Serial.println("Running Platform tests...");
  int testPassed = 0;
  
  Platform platform;
  
  // Тест 1: Старт платформы
  platform.start();
  // Здесь нужно проверить состояние I2C устройств (можно добавить mock)
  Serial.println("Test 1: Platform start command sent");
  
  // Тест 2: Стоп платформы
  platform.stop();
  Serial.println("Test 2: Platform stop command sent");
  
  // Для реального тестирования нужно проверять состояние устройств
  Serial.println("Platform Tests: Manual verification required\n");
}

void testTern() {
  Serial.println("Running Tern tests...");
  
  Tern tern;
  
  // Тест 1: Старт подъемника
  tern.start();
  Serial.println("Test 1: Tern start command sent");
  
  // Тест 2: Стоп подъемника
  tern.stop();
  Serial.println("Test 2: Tern stop command sent");
  
  // Тест 3: Остановка подъема
  tern.lift_stop();
  Serial.println("Test 3: Tern lift stop command sent");
  
  Serial.println("Tern Tests: Manual verification required\n");
}
