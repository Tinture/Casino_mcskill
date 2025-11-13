local gpu = require("component").gpu
local computer = require("computer")
local term = require("term")
event = require("event")
local admins = { "Tintur" }  -- Tintur как главный админ
local shell = require("shell")

if not require("filesystem").exists("/lib/mycasinodb.lua") then
    shell.execute("wget -q https://raw.githubusercontent.com/Tinture/Casino_mcskill/main/mycasinodb.lua /lib/mycasinodb.lua")
end

local removeUsers = function(...)
    for i = 1, select("#", ...) do
        computer.removeUser(select(i, ...), nil)
    end
end

function updateFromGitHub()
    if not require("filesystem").exists("/home/appInfo.lua") then
        return
    end
    local app = loadfile("/home/appInfo.lua")()
    shell.execute("wget -fq https://raw.githubusercontent.com/Tinture/Casino_mcskill/main/APPS/" .. app.name .. ".lua /home/app.lua")
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
        if admins[i] == "Tintur" then
            gpu.set(51, 8 + i, admins[i] .. " 👑")  -- Корона для главного админа
        else
            gpu.set(51, 8 + i, admins[i])
        end
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
io.write("URL сервера [http://192.168.0.177:5000]: ")
gpu.setForeground(0x000000)
local server_url = io.read()
if server_url == "" then
    server_url = "http://192.168.0.177:5000"  -- Ваш IP по умолчанию
end
Connector = MyCasinoDB:new(server_url)

print("🔗 Проверка соединения с сервером...")
print("🌐 Адрес: " .. server_url)
local test_balance = Connector:get("Tintur")  -- Проверяем соединение через админа
if test_balance then
    print("✅ Соединение с сервером установлено!")
    print("👑 Администратор системы: Tintur")
    print("💰 Баланс администратора: " .. tostring(test_balance))
else
    print("❌ Ошибка соединения с сервером!")
    print("⚠️  Проверьте:")
    print("   - Запущен ли сервер на ПК")
    print("   - Правильность IP адреса")
    print("   - Доступность порта 5000")
end

removeUsers(computer.users())
while true do
    gpu.setForeground(0xffffff)
    result, errorMsg = pcall(loadfile("/home/app.lua"))
    removeUsers(computer.users())
    drawError(errorMsg)
end
