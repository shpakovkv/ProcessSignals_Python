Консольные приложения SignalProcess и PeakProcess
=================================================

### Разделы:
1. [Введение](#введение)
1. [Структура входных файлов](#структура-входных-файлов)
1. [Чтение, объединение и сохранение файлов](#чтение-и-сохранение-файлов)
1. [Изменение данных](#изменение-данных)
1. [Поиск пиков](#поиск-пиков)
1. [Построение графиков](#построение-графиков)
1. [Термины](#термины)

Введение
--------

Программа предназначена в первую очередь для работы с фалами, записанными цифровыми запоминающими осциллографами, но может применяться для обработки любых данных, представляющих собой последовательность пар чисел (Xi, Yi).

### Ключевые особенности:

* простое считывание данных в бинарном формате WFM и в текстовом формате (CSV, TXT, DAT и т.д.)
* независимое умножение столбцов на указанный коэффициент и вычитаение указанного значения (Yi = Yi * M - D)
* привязка начала отсчета по времени к переднему фронту выбранного сигнала (необходимо для корректного отображения сигналов разных выстрелов на одном графике)
* автоматическое вычитание постоянной составляющей из амплитуды выбранных сигналов (корректировка нулевого уровня)
* поиск пиков сигналов с гибкой настройкой параметров поиска реальных (настоящих) пиков и исключения из результатов паразитных (ненастоящих) пиков
* автоматичская группировка совпадающих по времени пиков (на разных сигналах)
* построение графиков кривых (одной или нескольких), с отмеченными пиками и без


Структура входных файлов
------------------------

В текстовых файлах типа CSV, TXT и DAT данные по кривым (записанным осциллографом или другим устройством/программой сигналам) хранятся в виде двумерной таблицы - по два столбца на кривую (отсчеты по времени и амплитуде). Ниже приведены некоторые особенности структуры таких файлов:

* Некоторые осциллографы (например Rohde&Schwarz HMO 3000 series) записывают в файл один столбец с отсчетами по времени и несколько с отсчетами по амплитуде (для экономии места). Каждая строка файла - это одна строка таблицы. 

* Столбцы разделены специальным символом - "разделителем" (у разных устройств/программ записи разделитель может различаться). 

* Количество строк в файлах зависит от настроек устройства/программы, с помощью которого этот файл был записан. 

* Первые несколько строк файла могут содержать текстовую информацию о содержимом файла (названия столбцов, количество строк, параметры записи, модель устройсва или версия программы и т.д.).

Программа SignalProcess сама подбирает все параметры считывания (разделитель столбцов, разделитель разрядов, количество строк заголовка), удаляет пустые столбцы и дублирует столбец времени для файлов, в которых записан один столбец времени и несколько столбцов амплитуд (**Важно:** файл с такой структурой будет прочитан корректно, только если в нем записано четное количество столбцов амплитуд). 


Чтение и сохранение файлов
--------------------------

Программа может читать бинарные файлы WFM и текстовые файлы CSV, TXT, DAT и т.д. С помощью программы вы можете считать данные из нескольких файлов, подкорректировать их (см. следующий раздел) и сохранить в один CSV файл для хранения корректных данных и последующей обработки сторонними программами.

#### Одина группа файлов:
Для считывания одного файла с данными или нескольких файлов с их последующим объединением выполните следующие действия:
1. Через флаг '-d', '--src' или '--source-dir' укажите путь до файлов с данными.
2. Вы можете задать входные файлы двумя способами: 
  * Для считывания нескольких файлов используйте флаг '-f' или '--input-files' и укажите через пробел имена файлов.
  * Для считывания всех файлов, находящихся в папке используйте флаг '-g' или '--grouped-by' и укажите в качестве размера группы число файлов в папке. Также через флаг '-e', '--ext' или '--extension' укажите расширения файлов, которые необходимо считать (файлы с другими расширениями будут проигнорированны).
3. Для сохранения данных укажите флаг '-s' или '--save'.
4. Вы можете указать папку для сохранения выходных файлов через флаг '-t' или '--save-to'. Если на вход программе был подан один файл, а выходная папка не указана, то при сохранении данных файл будет перезаписан.
5. Имя выходного файла соответствует первому входному файлу, но вы можете указать имя выходного файла в явном виде через флаг '-o' или '--output'.

Для считывания части данных из файлов используйте флаг '--partial-import' и укажите три числа (**Start**, **Step**, **Count**). **Start** - индекс (начинается с 0) первой строки данных в файле, с которой необходимо начать считывание данных. **Step** - шаг считывания. **Count** - количество строк с данными, которые надо считать (укажите -1 для считывания до конца файла).

Для уменьшения количества выводимой на экран информации в процессе работы программы укажите флаг '--silent'.

##### Примеры:
```
python SignalProcess.py --src '/home/UserName/Experiment Data/Source' --input-files first_detector.csv second_detector.txt --partial-import 1000 1 -1 --save --silent
```
```
python SignalProcess.py --src '/home/UserName/Experiment Data/Source' --grouped-by 2 --extension csv txt --save --save-to '/home/UserName/Experiment Data/Final/'
```
#### Несколько групп фалов:
Если в ходе экспериментов данные с датчиков записывались несколькими запоминающими устройствами, то мы имеем **N*K** файлов, где **N** - количество выстрелов (см. Термины), **K** - количество запоминающих устройств. Для корректного считывания данных из этих файлов вы можете вручную указать порядок считывания файлов используя N флагов '--input-files', указывая в каждом K имен файлов (в правильном порядке), относящихся к одному выстрелу. 

Либо вы можете просто указать размер группы файлов **K** через флаг '--grouped-by', заранее пронумеровав файлы определенным образом:

[**prefix**][**N-number**][**separator**][**K-number**][**postfix**].[**ext**]

**prefix** - одинаковый для всех файлов префикс имени файла. Должен заканчиваться нецифровым символом. Может отсутствовать.

**N-number** - номер выстрела. Записывается с ведущими нулями, т.к. количество символов в номере должно быть одинаково для всех файлов.

**separator** - любая последовательность символов, разделяющая числа N-number и K-number.

**K-number** - номер или название записываэщего устройства. Количество символов должно быть одинаково для всех файлов.

**postfix** - одинаковый для всех файлов постфикс имени файла. Должен начинаться с нецифрового символа. Может отсутствовать.

**ext** - расширение файла.

Пример имени файла: "0047-osc01-signals.wfm" == [][0047][-osc][01][-signals].[wfm]

Пример команды для считывания данных, записанных четырьмя осциллографами в файлы форматов CSV, DAT, WFM:
```
python SignalProcess.py --src 'C:\Experiment Data\Source' --grouped-by 4 --extension csv dat wfm --save --save-to 'C:\Experiment Data\Final'
```
При выполнении этой команды программа будет на каждом цикле считывать данные очередного выстрела из разных файлов и сохранять их одним CSV файлом в указанной папке.

##### Альтернативный вариант нумерации файлов.
Вы можете пронумеровать файлы в первую очередь по номеру/названию записывающего устройства **K** и во вторую очередь - по номеру выстрела **N**:

[**prefix**][**K-number**][**separator**][**N-number**][**postfix**].[**ext**]

В этом случае необходимо указать флаг '--sorted-by-channel':
```
python SignalProcess.py --src 'C:\Experiment Data\Source' --grouped-by 4 --sorted-by-channel --extension csv dat wfm --save --save-to 'C:\Experiment Data\Final'
```

Изменение данных
----------------
*описание в разработке*


Поиск пиков
-----------
*описание в разработке*


Построение графиков
-------------------
*описание в разработке*


Термины 
-------

* **Выстрел** - событие, записанное одним или несколькими осциллографами (или другими измерительными устройствами) в виде сигналов с датчиков

* **Группа файлов** - совокупность данных (сигналов с измерительных устройств), записанных в одном выстреле в виде нескольких отдельных файлов

* **Кривая** - сигнал с датчика, записанный осциллографом (или другим измерительным устройством) в виде последовательности отсчетов по времени и амплитуде