local input_object = {{'1', 'Luke Bayne', -4, -29, {-1, -1, 1, 0, 0, 0, -1, -1, -1}}, {'2', "Austin D'Alessandro", -7, -22, {0, -1, -1, -1, -1, -1, -1, -1, 0}}, {'3', 'Blake Houston', -2, -18, {0, 0, 1, -1, -1, 0, -1, 0, 0}}, {'4', 'Tim Bohan', -3, -17, {0, 0, 1, 0, -1, -1, -1, -1, 0}}, {'5', 'Jade Brady', -4, -16, {0, 0, -1, 0, 0, -1, 0, -1, -1}}, {'5', 'Patrick Robinson', -3, -16, {0, -1, 1, -1, 0, 1, -1, -1, -1}}, {'5', 'Matthew Noblet', -2, -16, {0, -1, 0, -1, 0, -1, 1, 0, 0}}, {'8', 'Christopher Finn', -3, -13, {0, -1, 0, -1, 0, 0, 0, -1, 0}}, {'9', 'Darren Stace-Smith', -4, -11, {0, 0, 0, -1, -1, 0, -1, -1, 0}}, {'10', 'Dan Frost', -1, -9, {0, 0, -1, 1, 0, -1, 0, 0, 0}}, {'11', 'Ryan Hart', -2, -8, {0, 0, 0, -1, -1, -1, 0, 1, 0}}, {'12', 'Aidan Howard', -2, -7, {0, 1, -1, -1, 0, 0, 0, -1, 0}}, {'12', 'Ryan Michell', -1, -7, {0, -1, 0, -1, 0, 0, 2, -1, 0}}, {'14', 'Søren Støttrup', -2, -3, {0, 0, -1, 0, -1, 0, 1, -1, 0}}, {'15', 'Rhys Wisniewski', 'E', '+6', {0, 0, 1, -1, 0, 0, 1, -1, 0}}, {'16', 'Nathan Parish', -1, '+7', {0, 0, 1, -1, 0, -1, 0, 0, 0}}, {'17', 'Ryan Dear', -2, '+8', {0, 0, 0, -1, -1, 1, 0, -1, 0}}, {'18', 'Adam Rigby', '+4', '+10', {0, 2, 1, 1, 0, -1, 0, 0, 1}}, {'19', 'Atticus Ariston', 'E', '+14', {0, 1, -1, 0, 
0, 0, 0, -1, 1}}}

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