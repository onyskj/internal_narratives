// ------------> Open-ended question <---------------
let oq_time = 100//100
let oq_min_words = 30 //30

let oq_preamble_text = "ANSWER ALL IN ONE GO"
let oq_preamble = `<div id="type_audio_preamble">
        <h4>${oq_preamble_text}</h4></div>`

// Baseline
let oq_baseline_text = "<p class='check_maybe'>Reflect about yourself over the past two weeks.</p>&#8213;<p>How would you describe your overall emotional well-being, including your mood, feelings, thoughts about yourself, and any changes in your behaviour or daily functioning?</p><p>Please provide examples of situations or experiences that best illustrate these aspects.</p>"
let oq_baseline_el = `<div id="type_qs">` + oq_baseline_text + `</div>`

let oq_mood_text = "<p>For the past two weeks, have you been bothered by your mood and how you felt generally? Were there any situations when you felt down, depressed, or hopeless?</p>"
let oq_mood_el = `<div id="type_qs">` + oq_mood_text + `</div>`

let oq_energy_text = "<p>Have you been bothered by your energy levels over the past two weeks? Can you recall situations when it comes to feeling tired/lively or low/high on energy?</p>"
let oq_energy_el = `<div id="type_qs">` + oq_energy_text + `</div>`

// Follow-up
let oq_fu_text = "<p class='check_maybe'>Reflect about yourself over the past two weeks.</p>&#8213;<p>How would you describe your overall emotional well-being, including your mood, feelings, thoughts about yourself, and any changes in your behaviour or daily functioning?</p><p>Please provide examples of situations or experiences that best illustrate these aspects.</p>"
let oq_fu_el = `<div id="type_qs">` + oq_fu_text + `</div>`

// Positive peturbation
let pospert_time = 120//130
let pospert_min_words = 30 //30
// let oq_pospert_text = "<p class='check_maybe'>Revisit both your responses about yourself from before.</p><p>Now, reframe them more positively and rewrite them here.</p>"
let oq_pospert_text = "<p class='check_maybe'>Revisit both your responses from before about your mood, feelings and energy levels.</p><p>Now, reframe them more positively and rewrite them here.</p><p>Remember to give examples of situations or experiences that best illustrate these.</p>"



let oq_pospert_el = `<div id="type_qs">` + oq_pospert_text + `</div>`
