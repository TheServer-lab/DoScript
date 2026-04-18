global_variable = score, label, total

score = 82
label = ""
total = 0

if score >= 90
    label = "A"
else_if score >= 80
    label = "B"
else_if score >= 70
    label = "C"
else
    label = "Needs work"
end_if

loop 4 as i
    total = total + i
end_loop

say 'Grade: {label}'
say 'Loop total: {total}'
