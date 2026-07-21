// ------------> Practice typing <---------------
let practice_min_words = 5
let practice_time = 20// 20
let practice_instr_time = 30 //30

let type_practice_instr = `
<div class="pre_trial_instr">
    <!--<h4>In the study, you will have to listen to</h4>-->
    <h3>We will first check whether you can hear the sounds well.</h3>
    <h4>Listen carefully, and then type exactly what you hear.</h4>
    &#8213;
    <p>You will have to pass these checks to proceed with the study.</p>
    <p>Adjust the volume accordingly.</p>
    <br>
    <!--<h3>You will now practice the TYPE task.</h3>-->
    <!--<h4>Please read each question carefully.</h4>-->
        <div id="story_instr_box"><p style="color:black">Type as usual &ndash; each word will be automatically submitted after you press the "Space" key.</p>
        <p>Submit everything once you think you got it correctly.</p>
    <!--    <p>Type at least the required minimum of words before time runs out!</p>-->
        </div>
        <br>
    <!--    <p class="next_page">Press <b>n</b> to proceed.</p>-->
        <p class="next_page"></p>
    </div>
`

// let oq_practice_preamble_text = "TYPE WHAT YOU'VE HEARD"
let oq_practice_preamble_text = "TYPE WHAT YOU HEARD"
let oq_practice_preamble = `<div id="type_audio_preamble">
        <h4>${oq_practice_preamble_text}</h4></div>`

let practice_texts = {
    'type_practice_1': ['five', 'dogs', 'are', 'drinking', 'water'],
    // 'type_practice_2': ['sweet', 'juice', 'in', 'a', 'glass']
}


// ------------> Recreate task <---------------
let recreate_time = 40 //40
let recreate_min_words = 15 //10

let recreate_instr_time = 40 //40
let recreate_instr_text = `
    <div class="pre_trial_instr">
    <h3>Next, you will listen to diary entries from the same person.</h3>
    <!--<h4>Listen carefully, and imagine being that person.</h4>-->
    <h4>As you listen, put yourself in their shoes and imagine you are an actor playing their character.</h4>
    <!--<h4>Put yourself in their shoes as they were writing these entries.</h4>-->
        &#8213;
    <h4 style="color:red">You will need to reenact each entry by typing what you've heard.</h4>
        <div id="story_instr_box">
        <p style="color:black">Be as detailed as possible, but don't worry about typos or memorising word by word.</p>
         <p>Focus on richly capturing the gist from a first-person perspective.</p></div>
         <br>
    <p class="next_page"></p>
    </div>
`

let recreate_preamble_text = `RECREATE DIARY ENTRY`
let recreate_preamble = `<div id="type_audio_preamble">
        <h4>${recreate_preamble_text}</h4></div>`

// ------------> Act task <---------------
let act_time = 180 //120 - 200
// let act_min_words = 10 //10
let act_min_words_total = 100 //100

let act_instr_time = 40 //40
let example_counter2 = `
<div id="word_counter2_ex" class="counter_example">
<span id="n_words">8</span><span>/</span><span id="min_words">30</span>
</div>
`
let act_instr_text = `
    <div class="pre_trial_instr">
    <h3>Keep acting the same character.</h3>
    <h4><span id='act_preamble_hl'>This time be creative and come up with what their next diary entries could look like.</span></h4>
    <h4>Be as detailed as possible!</h4>
<!--    <p>Keep typing until the time runs out</p>-->
    <br>
        <div id="story_instr_box"><p style="color:black">
    <!--    Don't worry about memorising word by word.</p>-->
    <p>If you've exhausted one train of thought, start another while staying in character.</p>
    <p style="color:black">Keep typing until the time runs out.</p>
<!--        <p style="color:black">Be as detailed as possible!</p>-->
    <!--     <p>Just focus on capturing the gist.</p>-->
         </div>
         <br>
    <p class="next_page"></p>
    </div>
`

let act_preamble_text = "<span id='act_preamble_hl'>CREATE NEW</span> DIARY ENTRIES"
let act_preamble = `<div id="type_audio_preamble">
        <h4>${act_preamble_text}</h4>
</div>`
