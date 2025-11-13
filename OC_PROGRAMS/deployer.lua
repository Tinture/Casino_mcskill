local component = require("component")
if not component.isAvailable("internet") then
    io.stderr:write("Требуется интернет карта!")
    return
end

local computer = require("computer")
local shell = require("shell")
local filesystem = require("filesystem")

local GAMES = {
    { "Checker", "app_Checker" },
    { "Roulette", "game_Roulette" },
    { "Black Jack", "game_Black_jack" },
    { "Minesweeper", "game_Minesweeper" },
    { "Video Poker", "game_video_poker" },
    { "More/Less", "game_More_less" },
    { "Labyrinth", "game_Labyrinth" }
}

local function writeToFile(path, content)
    local file = io.open(path, "w")
    file:write(content)
    file:close()
end

local function downloadFromGitHub(path, url)
    print("📥 Скачивание: " .. path)
    return shell.execute("wget -q " .. url .. " " .. path)
end

print("🎰 === TURBO HAPPINESS CASINO ===")
print("👑 Администратор: Tintur")
print("🌐 Сервер: http://192.168.0.177:5000")
print("=" .. string.rep("=", 40))

-- Скачиваем базу данных
downloadFromGitHub(
    "/lib/mycasinodb.lua",
    "https://raw.githubusercontent.com/Tinture/Casino_mcskill/main/mycasinodb.lua"
)

-- Скачиваем лаунчер
downloadFromGitHub(
    "/home/1",
    "https://raw.githubusercontent.com/Tinture/Casino_mcskill/main/launcher.lua"
)

-- Выбор игры
print("\n🎮 Выберите игру для установки:")
for i = 1, #GAMES do
    print(i .. ". " .. GAMES[i][1])
end
io.write("Введите номер: ")
local choice = tonumber(io.read())

if choice and choice >= 1 and choice <= #GAMES then
    local game = GAMES[choice]
    
    -- Скачиваем выбранную игру
    downloadFromGitHub(
        "/home/app.lua",
        "https://raw.githubusercontent.com/Tinture/Casino_mcskill/main/APPS/" .. game[2] .. ".lua"
    )
    
    -- Сохраняем информацию о приложении
    writeToFile("/home/appInfo.lua", 
        'return {name="' .. game[2] .. '", label="' .. game[1] .. '", admin="Tintur"}'
    )
    
    print("\n" .. string.rep("=", 40))
    print("✅ УСТАНОВКА ЗАВЕРШЕНА!")
    print("🎮 Игра: " .. game[1])
    print("👑 Администратор: Tintur")
    print("🌐 Сервер: http://192.168.0.177:5000")
    print("🚀 Запуск: /home/1")
    print("=" .. string.rep("=", 40))
else
    print("❌ Неверный выбор!")
end
