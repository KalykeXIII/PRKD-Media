local input_object = {{'1', 'Rhys Wisniewski', -1, -1, {0, -1, 0, 0, 0, 0, 0, 0, 0}}, {'T2', 'Jade Brady', 'E', 'E', {-1, 0, 0, 3, 0, -1, -1, 0, 0}}, {'T2', 'Dan Frost', 'E', 'E', {0, 0, 0, 0, 0, 0, 0, 0, 0}}, {'T2', 'Ryan Hart', 'E', 'E', {0, 1, 0, -1, 0, 0, 0, 0, 0}}, {'T2', 'Blake Houston', 'E', 'E', {-1, 1, -1, 2, 0, 0, 0, -1, 0}}, {'T2', 'Tim Bohan', 'E', 'E', {0, 0, 0, 0, 0, 0, -1, 1, 0}}, {'T2', 'Aaron Moreton', 'E', 'E', {-1, 1, 0, 0, 0, -1, 0, 1, 0}}, {'T8', 'Adam Rigby', '+1', '+1', {1, 1, 0, 0, 0, -1, 0, 1, -1}}, {'T8', 'Clayton Beck', '+1', '+1', {2, -1, 0, 0, 0, 0, 0, 0, 0}}, {'T8', 'Ryan Budge', '+1', '+1', {0, 0, 0, 0, 0, 0, 0, 1, 0}}, {'T8', "Austin D'Alessandro", '+1', '+1', {1, -1, 2, 1, 1, 0, -1, -1, -1}}, {'12', 'Patrick Robinson', '+2', '+2', {0, 1, 0, 0, 0, 1, 1, -1, 0}}, {'T13', 'Paul Phillips', '+3', '+3', {1, 0, 1, 0, 0, 0, 0, 1, 0}}, {'T13', 'Abra Garfield', '+3', '+3', {1, 0, 0, 3, -1, 0, -1, 2, -1}}, {'T13', 'Jarrath Sweetten', '+3', '+3', {1, 0, 2, 0, 0, 1, -1, 0, 0}}, {'T13', 'Nicholas Halstead', '+3', '+3', {0, 0, 1, 1, 2, 0, -1, 0, 0}}, {'17', 'David Perry', '+4', '+4', {1, 1, 2, 1, -1, 0, 0, 0, 0}}, {'18', 'Stephen Kearney', '+5', '+5', {0, 1, 1, 2, 0, -1, 0, 2, 0}}, {'T19', 'Alex Tame', '+6', '+6', {1, 1, 0, 5, 0, -1, -1, 1, 0}}, {'T19', 'Sarah Lee', '+6', '+6', {1, 0, 1, 1, 0, 1, 0, 1, 1}}, {'T19', 'Michal Durand', '+6', '+6', {0, 0, 3, 1, 0, 0, 0, 3, -1}}, {'22', 'Chris Hill', '+7', '+7', {3, 0, 1, 2, 0, -1, 0, 1, 1}}, {'23', 'Leith Brodie', '+8', '+8', {1, 0, 1, 6, 0, 1, 0, -1, 0}}, {'24', 'Connor Donnelly', '+9', '+9', {0, 2, 1, 5, 0, -1, 1, 1, 0}}}

function UpdateLeaderboard(object)
    for i in pairs(object) do 
        print(object[i][1], object[i][2], object[i][3], object[i][4])
        -- Update all elements in the row
        UpdateLeaderboardRow(i, object[i][1], object[i][2], object[i][3], object[i][4])
    end
end

function UpdateLeaderboardRow(row, position, name, round, total)
    -- Firstly get the lookups for all of the necessary fields
    local pos_lookup = 'Player' .. tostring(row) .. '_Pos'
    local name_lookup = 'Player' .. tostring(row) .. '_Name'
    local round_lookup = 'Player' .. tostring(row) .. '_Round'
    local total_lookup = 'Player' .. tostring(row) .. '_Total'

    -- 
    local textObjects = comp:GetToolList(false, "TextPlus")
    for k, txt in ipairs(textObjects) do
        if txt.Name == pos_lookup then
            -- Update the content of the object
            txt.StyledText:SetExpression('Text("' .. position .. '")')
        end
        if txt.Name == name_lookup then
            -- Update the content of the object
            txt.StyledText:SetExpression('Text("' .. name .. '")')
        end
        if txt.Name == round_lookup then
            -- Update the content of the object
            txt.StyledText:SetExpression('Text("' .. round .. '")')
        end
        if txt.Name == total_lookup then
            -- Update the content of the object
            txt.StyledText:SetExpression('Text("' .. total .. '")')
        end
    end
end

UpdateLeaderboard(input_object)