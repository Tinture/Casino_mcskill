local internet = require("internet")
local serialization = require("serialization")

MyCasinoDB = {}

function MyCasinoDB:new(server_url)
    local obj = {}
    obj.server_url = server_url or "http://192.168.0.177:5000"
    
    -- Убираем слеш в конце URL если есть
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
            print("Ошибка запроса баланса: " .. tostring(response))
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
            print("Ошибка запроса времени: " .. tostring(response))
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
            print("Ошибка списания: " .. tostring(response))
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
            print("Ошибка начисления: " .. tostring(response))
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
            print("Ошибка запроса топа: " .. tostring(response))
            return {}
        end
    end

    setmetatable(obj, self)
    self.__index = self
    return obj
end