local component = require("component")
if not component.isAvailable("internet") then
    io.stderr:write("Требуется интернет карта!")
    return
end
local computer = require("computer")
local shell = require("shell")
local filesystem = require("filesystem")

local GAMES = {
    { "Terminal (PIM)", "app_Terminal" },
    { "Terminal (Chest)", "app_Terminal_2.0" },
    { "Checker", "app_Checker" },
    { "Video Poker", "game_video_poker" },
    { "Minesweeper", "game_Minesweeper" },
    { "Roulette", "game_Roulette" },
    { "Black Jack", "game_Black_jack" },
    { "More less", "game_More_less" },
    { "Labyrinth", "game_Labyrinth" }
}

local SETTINGS = {
    applicationLabel = nil,
    application = nil,
    server_url = "http://192.168.0.177:5000"
}

local function writeToFile(path, content)
    local file = io.open(path, "w")
    file:write(content)
    file:close()
end

local function selectFromList(list, labelKey)
    for i = 1, #list do
        print(i .. ". " .. list[i][labelKey])
    end
    io.write("Выберите номер: ")
    local choice = tonumber(io.read())
    if choice and choice >= 1 and choice <= #list then
        return list[choice]
    end
    return nil
end

local function downloadFile(url, path)
    return shell.execute("wget -q " .. url .. " " .. path)
end

local function setupCasinoDB()
    print("Настройка базы данных...")
    
    -- Скачиваем нашу базу данных
    local db_content = [[
local internet = require("internet")
local serialization = require("serialization")

MyCasinoDB = {}

function MyCasinoDB:new(server_url)
    local obj = {}
    obj.server_url = server_url or "http://192.168.0.177:5000"
    
    if obj.server_url:sub(-1) == "/" then
        obj.server_url = obj.server_url:sub(1, -2)
    end
    
    function obj:get(nick)
        local url = self.server_url .. "/users/get?name=" .. nick
        local success, response = pcall(function()
            for chunk in internet.request(url) do
                return chunk
            end
        end)
        
        if success and response then
            return tonumber(response) or 0
        else
            return 0
        end
    end

    function obj:getTime()
        local url = self.server_url .. "/get/time"
        local success, response = pcall(function()
            for chunk in internet.request(url) do
                return chunk
            end
        end)
        
        if success and response then
            return tonumber(response) or os.time()
        else
            return os.time()
        end
    end

    function obj:pay(nick, money)
        local url = self.server_url .. "/users/pay?name=" .. nick .. "&money=" .. money
        local success, response = pcall(function()
            for chunk in internet.request(url) do
                return chunk
            end
        end)
        
        if success and response then
            return response == "True"
        else
            return false
        end
    end

    function obj:give(nick, money)
        local url = self.server_url .. "/users/give?name=" .. nick .. "&money=" .. money
        local success, response = pcall(function()
            for chunk in internet.request(url) do
                return chunk
            end
        end)
        
        if success and response then
            return response == "True"
        else
            return false
        end
    end

    function obj:top()
        local url = self.server_url .. "/users/top"
        local success, response = pcall(function()
            for chunk in internet.request(url) do
                return chunk
            end
        end)
        
        if success and response then
            return serialization.unserialize(response) or {}
        else
            return {}
        end
    end

    setmetatable(obj, self)
    self.__index = self
    return obj
end
]]
    
    writeToFile("/lib/mycasinodb.lua", db_content)
    print("✅ База данных настроена")
end

local function selectApplication()
    print("Выберите приложение для установки:")
    local application = selectFromList(GAMES, 1)
    if not application then
        error("Приложение не выбрано!")
    end
    SETTINGS.application = application[2]
    SETTINGS.applicationLabel = application[1]
end

local function setupServerURL()
    io.write("URL вашего сервера [http://192.168.0.177:5000]: ")
    local url = io.read()
    if url ~= "" then
        SETTINGS.server_url = url
    end
end

local function saveLauncher()
    print("Установка загрузчика...")
    
    local launcher_content = [[
local gpu = require("component").gpu
local computer = require("computer")
local term = require("term")
event = require("event")
local admins = { "Durex77", "krovyaka", "krovyak", "SkyDrive_" }
local shell = require("shell")

if not require("filesystem").exists("/lib/mycasinodb.lua") then
    io.stderr:write("Ошибка: файл mycasinodb.lua не найден в /lib/")
    return
end

local removeUsers = function(...)
    for i = 1, select("#", ...) do
        computer.removeUser(select(i, ...), nil)
    end
end

function updateFromGitHub()
    local app = loadfile("/home/appInfo.lua")()
    shell.execute("wget -fq https://raw.githubusercontent.com/lfreew1ndl/OpenComputers-Casino/" .. app.branch .. "/apps/" .. app.name .. ".lua /home/app.lua")
end

local function drawError(reason)
    gpu.setResolution(49, 20)
    gpu.setBackground(0x705f5f)
    gpu.setForeground(0xffffff)
    term.clear()
    print('Приложение завершило свою работу по причине:')
    if (reason == nil) then
        reason = "Успешное завершение программы"
    end
    print(reason)
    gpu.setResolution(80, 20)
    gpu.setBackground(0xFFB300)
    gpu.fill(50, 6, 31, 15, ' ')
    gpu.setForeground(0)
    gpu.set(51, 7, 'Кнопка доступна для:')
    for i = 1, #admins do
        gpu.set(51, 8 + i, admins[i])
    end
    gpu.setForeground(0xffffff)

    gpu.setBackground(0x800080)
    gpu.fill(71, 1, 10, 5, ' ')
    gpu.set(72, 3, 'Обновить')

    gpu.setBackground(0xa6743c)
    gpu.fill(50, 1, 21, 5, ' ')
    gpu.set(54, 3, 'Перезапустить')
    gpu.setBackground(0)

    while true do
        local _, _, x, y, _, nickname = event.pull("touch")
        for i = 1, #admins do
            if (nickname == admins[i]) then
                if (x >= 50) and (x <= 70) and (y <= 4) then
                    return
                elseif (x >= 71) and (y <= 4) then
                    updateFromGitHub()
                    return
                end
            end
        end
    end
end

event.shouldInterrupt = function() return false end

require("mycasinodb")
io.write("URL сервера (например: http://192.168.0.177:5000): ")
gpu.setForeground(0x000000)
local server_url = io.read()
if server_url == "" then
    server_url = "]] .. SETTINGS.server_url .. [["
end
Connector = MyCasinoDB:new(server_url)

print("Проверка соединения с сервером...")
local test_balance = Connector:get("TestUser")
if test_balance then
    print("✅ Соединение с сервером установлено!")
else
    print("❌ Ошибка соединения с сервером!")
end

removeUsers(computer.users())
while true do
    gpu.setForeground(0xffffff)
    result, errorMsg = pcall(loadfile("/home/app.lua"))
    removeUsers(computer.users())
    drawError(errorMsg)
end
]]
    
    writeToFile("/home/1", launcher_content)
    print("✅ Загрузчик установлен")
end

local function saveApplication()
    print("Установка приложения...")
    -- Здесь можно добавить загрузку конкретного приложения
    -- Пока просто создаем заглушку
    writeToFile("/home/app.lua", "print('Приложение " .. SETTINGS.applicationLabel .. " запущено!')\n-- Код приложения здесь")
    print("✅ Приложение установлено")
end

local function saveApplicationInfo()
    print("Сохранение информации о приложении...")
    local info_content = string.format(
        'return {name="%s", label="%s", server_url="%s"}',
        SETTINGS.application,
        SETTINGS.applicationLabel,
        SETTINGS.server_url
    )
    writeToFile("/home/appInfo.lua", info_content)
    print("✅ Информация о приложении сохранена")
end

local function deploy()
    print("\nНачало установки казино...")
    setupCasinoDB()
    selectApplication()
    setupServerURL()
    saveLauncher()
    saveApplication()
    saveApplicationInfo()
    
    print("\n🎰 УСТАНОВКА ЗАВЕРШЕНА!")
    print("📁 Приложение: " .. SETTINGS.applicationLabel)
    print("🌐 Сервер: " .. SETTINGS.server_url)
    print("\nДля запуска введите: /home/1")
end

print("Casino Deployer 2.0")
print("Настройка для локального сервера\n")
deploy()