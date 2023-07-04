local courseDetails = {{3, 81, 1}, {3, 88, 3923}, {3, 87, 6825}, {4, 175, 9844}, {3, 111, 14400}, {3, 80, 17620}, {3, 65, 21347}, {3, 81, 24021}, {3, 84, 26780}}

local roundObject = {}
-- In this section give the player scores, followed by a list of the frames where these scores 'occur'
local player1 = {{2,0,0,0,0,1,0,-1,0}, {3735, 6494, 9652, 14338, 17456, 20770, 23906, 26180, 29991}}
local player2 = {{0,1,1,1,0,0,0,1,-1}, {3883, 6605, 9805, 14173, 17196, 21112, 23747, 26693, 29685}}
-- local player3 = {{1,1,-1,-1,0,0,2,0,-2}, {100, 400, 500, 580, 670, 730, 890, 950, 1000}}
-- local player4 = {{1,1,-1,-1,0,0,0,0,-2}, {100, 400, 500, 580, 670, 730, 890, 950, 1000}}
roundObject[1] = player1
roundObject[2] = player2
-- roundObject[3] = player3
-- roundObject[4] = player4

local parObject = {}
parObject[-3] = {'Albatross', {0.72,0.45,0.11}}
parObject[-2] = {'Eagle', {0.15,0.37,0.73}}
parObject[-1] = {'Birdie', {0.02,0.6,0.36}}
parObject[0] = {'Par', {0.42,0.41,0.42}}
parObject[1] = {'Bogey', {0.73,0,0.02}}
parObject[2] = {'Double Bogey', {0.57,0.1,0.72}}
parObject[3] = {'Triple Bogey', {0.51,0.38,0.32}}

-- This function takes the round object as input and turns it into an iterable table that is sorted chronologically
-- With the intention that iterating over this table will allow the animations to be run in the correct order in O(N) time
function GenerateRoundTimeline(round)
    local roundTimeline = {}
    for i, player in ipairs(round) do
        for j, score in ipairs(player[1]) do
            roundTimeline[player[2][j]] = {i, j, score}
        end
    end
    return roundTimeline
end

function CreatePlayerScorePath(playerRound, startScore)
    -- Instantiate the string we are going to output
    local scorePath = ''
    local scoreEnd = ''
    -- Check to see if the starting score is offset at all
    if not startScore then startScore = 0 end
    -- Iterate through the round to generate our path
    for i, score in ipairs(playerRound[1]) do
        -- For each subsequent hole we want to append a subsection of the paths
        -- Before doing so we must check the score abides by the style guide 
        -- = 0 -> E
        -- > 0 -> +
        -- Now generate a string to express the time change
        local scoreExpression = ''
        if startScore == 0 then
            scoreExpression = 'iif(time<' .. tostring(playerRound[2][i] + 1) .. ', Text("E"),'
        elseif startScore > 0 then
            scoreExpression = 'iif(time<' .. tostring(playerRound[2][i] + 1) .. ', Text("+' .. tostring(startScore) .. '"),'
        else
            scoreExpression = 'iif(time<' .. tostring(playerRound[2][i] + 1) .. ', Text(' .. tostring(startScore) .. '),'
        end
        -- Add the first hole to the starting score
        startScore = startScore + playerRound[1][i]
        scorePath = scorePath .. scoreExpression
        scoreEnd = scoreEnd .. ')'
    end
    -- Also add the score editing here
    local finalScore = ''
    if startScore == 0 then
        finalScore = 'Text("E")'
    elseif startScore > 0 then
        finalScore = 'Text("+' .. tostring(startScore) .. '")'
    else
        finalScore = 'Text(' .. tostring(startScore) .. ')'
    end
    scorePath = scorePath .. finalScore
    return scorePath .. scoreEnd
end

function GetFeetFromMetres(metres)
    return math.floor(metres * 3.2808)
end

-- Creates expression for the textual hole details based on an input courseDetails object including hole numbers, pars and associated meterage
function CreateCourseHolePath(courseDetails)
    -- Instantiate the string we are going to output
    local holeExpression = ''
    local distanceExpression = ''
    local expressionEnd = ''
    for i, holeDetail in ipairs(courseDetails) do
        local holeNumber = i
        local par = holeDetail[1]
        local distance_m = holeDetail[2]
        local distance_f = GetFeetFromMetres(distance_m)
        -- Also get the distance of the next hole
        local nextHoleStart = 1
        local holeExp = ''
        local distanceExp = ''
        local endString = ''
        if i < 9 then 
            nextHoleStart = courseDetails[i+1][3]
            holeExp = 'iif(time<' .. tostring(nextHoleStart) .. ', Text("' .. tostring(holeNumber) .. ' ' .. 'PAR ' .. tostring(par) ..'"),'
            distanceExp = 'iif(time<' .. tostring(nextHoleStart) .. ', Text("' .. tostring(distance_m) .. 'M ' .. tostring(distance_f) .. "'" .. '"),'
            expressionEnd = expressionEnd .. ')'
        else
            holeExp = 'Text("' .. tostring(holeNumber) .. ' ' .. 'PAR ' .. tostring(par) ..'")'
            distanceExp = 'Text("' .. tostring(distance_m) .. 'M ' .. tostring(distance_f) .. "'" .. '")'
        end
        holeExpression = holeExpression .. holeExp
        distanceExpression = distanceExpression .. distanceExp
    end
    holeExpression = holeExpression .. expressionEnd
    distanceExpression = distanceExpression .. expressionEnd
    return holeExpression, distanceExpression
end

-- This function is responsible for removing the holeDetails view at a given point in time (for outros, switches to and from leaderboards)
function ToggleHoleView(timing, on)
    -- Turn Off HoleViewMerge
    local mergeTools = comp:GetToolList(false, "Merge")
    for k, m in ipairs(mergeTools) do
        if m.Name == 'HoleViewMerge' and on == false then
            m:SetAttrs( { TOOLB_PassThrough = true } )
        elseif m.Name == 'HoleViewMerge' and on == true then
            m:SetAttrs( { TOOLB_PassThrough = false } )
        end
    end
    -- Remove Global Out the Background (HoleDetailsBG)
    -- local backgroundTools = comp:GetToolList(false, "Background")
    -- for k, bg in ipairs(backgroundTools) do
    --     if bg.Name == 'HoleDetailsBG' then
    --         bg:SetInput("GlobalOut", timing)
    --     end
    -- end
end

-- Takes input of the players round and the current hole and outputs their current score
-- TODO: Add support for multi-round tournaments adding an offset
function CalculateScore(playerHoles, hole)
    local sum = 0
    for i, v in ipairs(playerHoles) do
        if v <= hole then sum = sum + v end
    end
    return sum
end

-- Takes the player and hole completed and their score for the hole as input
-- Changes the background colour of the hole for teh given player
function ChangeHoleBackground(player, hole, holeScore, timing)
    local backgroundTools = comp:GetToolList(false, "Background")
    for k, bg in ipairs(backgroundTools) do
        if bg.Name == player .. '_' .. tostring(hole) .. 'B_1' then
            -- Set the colour based on the score
            if not holeScore then
                bg:SetInput("TopLeftRed", 0)
                bg:SetInput("TopLeftGreen", 0)
                bg:SetInput("TopLeftBlue", 0)
                bg:SetInput("TopLeftAlpha", 0)
            else
                bg:SetInput("TopLeftRed", holeScore[2][1])
                bg:SetInput("TopLeftGreen", holeScore[2][2])
                bg:SetInput("TopLeftBlue", holeScore[2][3])
                bg:SetInput("TopLeftAlpha", 1)
            end
            -- Change the GlobalIn based of the input
            bg:SetInput("GlobalIn", timing)
        end
    end
end

function SetPlayerScorePath(player, scorePath)
    local textTools = comp:GetToolList(false, "TextPlus")
    for l, txt in ipairs(textTools) do
        if txt.Name == player .. '_Score' then
            -- Before adding the Expression we want to nest it in a couple of display relevant conditions
            txt.StyledText:SetExpression(scorePath)
        end
    end
end

-- Edits the player display for the current hole
-- This includes the colour of the hole and the 'enabled' status as the hole is marked as completed
function EditHoleObject(player, hole, score)
    -- First change the colour of the score area based on the GetInputList
    ChangeHoleBackground(player, hole, score, 0)
end

-- Resets all scoreboard controllable items to default values
function ResetScoreboard()
    for i = 1, 2, 1 do
        local playerName = 'Player' .. tostring(i)
        for j = 1, 9, 1 do
            ChangeHoleBackground(playerName, j, false, 0)
        end
    end
end

function TestScoreboard(round)
    print('Main execution function running')
    print(comp.CurrentTime)
    -- Iterate through each player 
    for i, player in ipairs(round) do
        -- Create the player name for object referencing in Fusion (reliant on correctly inserting player scores above)
        local playerName = 'Player' .. tostring(i)
        local playerRound = player[1]
        -- For each player iterate through each hole
        for j, score in ipairs(playerRound) do
            -- For each hole first look at the score (relative to par)'
            local playerScore = parObject[score]
            -- Find the relevant hole indicator (based on player and hole)
            local totalScore = CalculateScore(playerRound, j)
            EditHoleObject(playerName, j, playerScore)
        end
    end
end

function AddScoreboardTimeline(round)
    -- Add the player score calculate and add the player score paths
    for i, player in ipairs(round) do
        local scorePath = CreatePlayerScorePath(player, 0)
        local playerName = 'Player' .. i
        SetPlayerScorePath(playerName, scorePath)
    end
    -- Generate the timeline friendly version of the round
    local finalRoundTimeline = GenerateRoundTimeline(round)
    -- Create an object to store all of the keys
    local timelineKeys = {}
    -- Iterate throguh the entrie round storing the timestamps
    for k in pairs(finalRoundTimeline) do table.insert(timelineKeys, k) end
    -- Order the timeline by time increasing
    table.sort(timelineKeys)
    -- Iterate through the timeline in chronological order
    for _, k in ipairs(timelineKeys) do
        -- Change keyframe start of the object based on the value k (time in seconds) - manual tuning can be done to account for frames being a more granular measure than seconds
        -- To do so access the Global In/Out of the background object
        local playerName = 'Player' .. finalRoundTimeline[k][1]
        local playerScore = parObject[finalRoundTimeline[k][3]]
        ChangeHoleBackground(playerName, finalRoundTimeline[k][2], playerScore, k)
        -- Create an iif chain for each player to add as an expression to the Score object
    end
end

-- ResetScoreboard()
-- TestScoreboard(roundObject)
-- AddScoreboardTimeline(roundObject)
-- local scorePath = CreatePlayerScorePath(roundObject[1], 0)
-- local playerName = 'Player' .. tostring(1)
-- SetPlayerScorePath(playerName, scorePath)
-- toggleHoleView(0, true)
print(CreateCourseHolePath(courseDetails))


