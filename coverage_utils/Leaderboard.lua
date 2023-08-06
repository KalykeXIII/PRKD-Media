local input_object = {{'T1', 'Tim Bohan', -6, -6, {0, 0, 1, -1, 0, -2, 0, 0, -1, 0, -1, -1, 0, 0, 0, -1, 1, -1}}, {'T1', 'Ryan Michell', -6, -6, {-1, 0, 0, 0, 0, 0, -1, 0, -1, 1, 0, -1, 0, -1, 0, 0, -1, -1}}, {'3', 'Ryan Hart', -4, -4, {1, 0, -1, 1, 1, -2, 0, 0, -1, -1, -1, -1, 0, 1, 0, -1, 1, -1}}, {'T4', 'Darren Stace-Smith', -3, -3, {0, -1, 2, 0, 0, -1, 0, 1, -1, 0, 0, 0, -1, 0, 0, -1, -1, 0}}, {'T4', 'Leo Dykes', -3, -3, {0, -1, 0, 0, 1, 2, -1, -1, -1, 2, 0, -1, 0, 0, -1, 0, -1, -1}}, {'6', 'Joshua Smith', -1, -1, {1, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, -1, 0, 0, 0, -1, 2}}, {'7', 'Ryan Dear', 'E', 'E', {0, 0, 1, -1, 0, -2, 0, 1, -1, 0, 1, 0, 0, 0, 0, -1, 0, 2}}, {'8', 'Aidan Howard', '+4', '+4', {1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, -1, -2, -1, 1}}}

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