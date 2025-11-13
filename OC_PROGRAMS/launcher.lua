local gpu = require("component").gpu
local computer = require("computer")
local term = require("term")
event = require("event")
local admins = { "Durex77", "krovyaka", "krovyak", "SkyDrive_" }
local shell = require("shell")

-- Загружаем нашу новую базу данных вместо durexdb
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

local function hideToken(s)
    if not s then
        return nil
    end
    return s:gsub("token=[ a-z0-9]*", "token=SECRET")
end

local function drawError(reason)
    gpu.setResolution(49, 20)
    gpu.setBackground(0x705f5f)
    gpu.setForeground(0xffffff)
    term.clear()
    print('Приложение завершило свою работу по причине:')
    if (reason == nil)
    then
        reason = "Успешное завершение программы"
    end
    print(hideToken(reason))
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

event.shouldInterrupt = function()
    return false
end

local computer = require("computer")
local pullSignalBackup = nil

local function DisableInterrupt()
  if pullSignalBackup ~= nil then
    return false
  end
  pullSignalBackup = computer.pullSignal
  computer.pullSignal = function(...)
    local tbl = {pcall(pullSignalBackup, ...)}
    return table.unpack(tbl, 2)
  end
  return true
end

local function EnableInterrupt()
  if pullSignalBackup == nil then
    return false
  end
  computer.pullSignal = pullSignalBackup
  pullSignalBackup = nil
  return true
end

-- Используем нашу новую базу данных
require("mycasinodb")
io.write("URL сервера (например: http://192.168.0.177:5000): ")
gpu.setForeground(0x000000)
local server_url = io.read()
if server_url == "" then
    server_url = "http://192.168.0.177:5000"
end
Connector = MyCasinoDB:new(server_url)

-- Проверяем соединение с сервером
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