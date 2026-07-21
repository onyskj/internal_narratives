
/*
-------------------------------------------------
------------> IDS-30 questions <---------------
-------------------------------------------------
*/


let ids30_preamble = `<div id="qs_preamble"><h3><u>Please select one response to each item that best describes you for the past seven days.</u></h3>
<!--            <h4>Then, submit your responses by clicking the button at the bottom of the page.</h4>-->
<!--        <p id='qs_preamble_disclosure'>(You can click on the question/statement to reset your answer.)</p>-->
        <p id='qs_preamble_disclosure'>(Please, scroll down to see all the questions.)</p>
        <p id="qsn_time">You have <span id="qsn_time_left"></span> seconds left</p>
                                ` + avoid_answer_qsn + `
        </div>`

let ids30_q1 = "Falling Asleep";
let ids30_q2 = "Sleep During the Night";
let ids30_q3 = "Waking Up Too Early";
let ids30_q4 = "Sleeping Too Much";
let ids30_q5 = "Feeling Sad";
let ids30_q6 = "Feeling Irritable";
let ids30_q7 = "Feeling Anxious or Tense";
let ids30_q8 = "Response of Your Mood to Good or Desired Events";
let ids30_q9 = "Mood in Relation to the Time of Day";
let ids30_q10 = "The Quality of Your Mood";
let ids30_q11 = "Appetite";
let ids30_q12 = "Weight";
let ids30_q13 = "Concentration/Decision Making";
let ids30_q14 = "View of Myself";
let ids30_q15 = "View of My Future";
let ids30_q16 = "Thoughts of Death or Suicide";
let ids30_q17 = "General Interest";
let ids30_q18 = "Energy Level";
let ids30_q19 = "Capacity for Pleasure or Enjoyment (excluding sex)";
let ids30_q20 = `Interest in Sex (Please Rate <u>Interest</u> not Activity)`;
let ids30_q21 = "Feeling slowed down";
let ids30_q22 = "Feeling restless";
let ids30_q23 = "Aches and pains";
let ids30_q24 = "Other bodily symptoms";
let ids30_q25 = "Panic/Phobic symptoms";
let ids30_q26 = "Constipation/diarrhea";
let ids30_q27 = "Interpersonal Sensitivity";
let ids30_q28 = "Leaden Paralysis/Physical Energy";


ids30_qs = [ids30_q1, ids30_q2, ids30_q3, ids30_q4, ids30_q5, ids30_q6, ids30_q7, ids30_q8, ids30_q9, ids30_q10, ids30_q11, ids30_q12, ids30_q13, ids30_q14, ids30_q15, ids30_q16, ids30_q17, ids30_q18, ids30_q19, ids30_q20, ids30_q21, ids30_q22, ids30_q23, ids30_q24, ids30_q25, ids30_q26, ids30_q27, ids30_q28]

let ids30_q1_responses = [
    "I never take longer than 30 minutes to fall asleep.",
    "I take at least 30 minutes to fall asleep, less than half the time.",
    "I take at least 30 minutes to fall asleep, more than half the time.",
    "I take more than 60 minutes to fall asleep, more than half the time."
];

let ids30_q2_responses = [
    "I do not wake up at night.",
    "I have a restless, light sleep with a few brief awakenings each night.",
    "I wake up at least once a night, but I go back to sleep easily.",
    "I awaken more than once a night and stay awake for 20 minutes or more, more than half the time."
];

let ids30_q3_responses = [
    "Most of the time, I awaken no more than 30 minutes before I need to get up.",
    "More than half the time, I awaken more than 30 minutes before I need to get up.",
    "I almost always awaken at least one hour or so before I need to, but I go back to sleep eventually.",
    "I awaken at least one hour before I need to, and can't go back to sleep."
];

let ids30_q4_responses = [
    "I sleep no longer than 7-8 hours/night, without napping during the day.",
    "I sleep no longer than 10 hours in a 24-hour period including naps.",
    "I sleep no longer than 12 hours in a 24-hour period including naps.",
    "I sleep longer than 12 hours in a 24-hour period including naps.",
];

let ids30_q5_responses = [
    "I do not feel sad.",
    "I feel sad less than half the time.",
    "I feel sad more than half the time.",
    "I feel sad nearly all of the time."
];

let ids30_q6_responses = [
    "I do not feel irritable.",
    "I feel irritable less than half the time.",
    "I feel irritable more than half the time.",
    "I feel extremely irritable nearly all of the time."
];

let ids30_q7_responses = [
    "I do not feel anxious or tense.",
    "I feel anxious (tense) less than half the time.",
    "I feel anxious (tense) more than half the time.",
    "I feel extremely anxious (tense) nearly all of the time."
];

let ids30_q8_responses = [
    "My mood brightens to a normal level which lasts for several hours when good events occur.",
    "My mood brightens but I do not feel like my normal self when good events occur.",
    "My mood brightens only somewhat to a rather limited range of desired events.",
    "My mood does not brighten at all, even when very good or desired events occur in my life."
];

let ids30_q9_responses = [
    "There is no regular relationship between my mood and the time of day.",
    "My mood often relates to the time of day because of environmental events (e.g., being alone, working).",
    "In general, my mood is more related to the time of day than to environmental events.",
    "My mood is clearly and predictably better or worse at a particular time each day."
];

let ids30_q10_responses = [
    "The mood (internal feelings) that I experience is very much a normal mood.",
    "My mood is sad, but this sadness is pretty much like the sad mood I would feel if someone close to me died or left.",
    "My mood is sad, but this sadness has a rather different quality to it than the sadness I would feel if someone close to me died or left.",
    "My mood is sad, but this sadness is different from the type of sadness associated with grief or loss."
];

let ids30_q11_responses = [
    "There is no change in my usual appetite.",
    "I eat somewhat less often or lesser amounts of food than usual.",
    "I feel a need to eat more frequently than usual.",
    "I eat much less than usual and only with personal effort.",
    "I regularly eat more often and/or greater amounts of food than usual.",
    "I rarely eat within a 24-hour period, and only with extreme personal effort or when others persuade me to eat.",
    "I feel driven to overeat both at mealtime and between meals."
];

let ids30_q12_responses = [
    "I have not had a change in my weight.",
    "I feel as if I've had a slight weight loss.",
    "I feel as if I've had a slight weight gain.",
    "I have lost 2 pounds or more.",
    "I have gained 2 pounds or more.",
    "I have lost 5 pounds or more.",
    "I have gained 5 pounds or more."
];

let ids30_q13_responses = [
    "There is no change in my usual capacity to concentrate or make decisions.",
    "I occasionally feel indecisive or find that my attention wanders.",
    "Most of the time, I struggle to focus my attention or to make decisions.",
    "I cannot concentrate well enough to read or cannot make even minor decisions."
];

let ids30_q14_responses = [
    "I see myself as equally worthwhile and deserving as other people.",
    "I am more self-blaming than usual.",
    "I largely believe that I cause problems for others.",
    "I think almost constantly about major and minor defects in myself."
];

let ids30_q15_responses = [
    "I have an optimistic view of my future.",
    "I am occasionally pessimistic about my future, but for the most part I believe things will get better.",
    "I'm pretty certain that my immediate future (1-2 months) does not hold much promise of good things for me.",
    "I see no hope of anything good happening to me anytime in the future."
];

let ids30_q16_responses = [
    "I do not think of suicide or death.",
    "I feel that life is empty or wonder if it's worth living.",
    "I think of suicide or death several times a week for several minutes.",
    "I think of suicide or death several times a day in some detail, or I have made specific plans for suicide or have actually tried to take my life."
];

let ids30_q17_responses = [
    "There is no change from usual in how interested I am in other people or activities.",
    "I notice that I am less interested in people or activities.",
    "I find I have interest in only one or two of my formerly pursued activities.",
    "I have virtually no interest in formerly pursued activities."
];

let ids30_q18_responses = [
    "There is no change in my usual level of energy.",
    "I get tired more easily than usual.",
    "I have to make a big effort to start or finish my usual daily activities (for example, shopping, homework, cooking or going to work).",
    "I really cannot carry out most of my usual daily activities because I just don't have the energy."
];

let ids30_q19_responses = [
    "I enjoy pleasurable activities just as much as usual.",
    "I do not feel my usual sense of enjoyment from pleasurable activities.",
    "I rarely get a feeling of pleasure from any activity.",
    "I am unable to get any pleasure or enjoyment from anything."
];

let ids30_q20_responses = [
    "I'm just as interested in sex as usual.",
    "My interest in sex is somewhat less than usual or I do not get the same pleasure from sex as I used to.",
    "I have little desire for or rarely derive pleasure from sex.",
    "I have absolutely no interest in or derive no pleasure from sex."
];

let ids30_q21_responses = [
    "I think, speak, and move at my usual rate of speed.",
    "I find that my thinking is slowed down or my voice sounds dull or flat.",
    "It takes me several seconds to respond to most questions and I'm sure my thinking is slowed.",
    "I am often unable to respond to questions without extreme effort."
];

let ids30_q22_responses = [
    "I do not feel restless.",
    "I'm often fidgety, wring my hands, or need to shift how I am sitting.",
    "I have impulses to move about and am quite restless.",
    "At times, I am unable to stay seated and need to pace around."
];

let ids30_q23_responses = [
    "I don't have any feeling of heaviness in my arms or legs and don't have any aches or pains.",
    "Sometimes I get headaches or pains in my stomach, back or joints but these pains are only sometimes present and they don't stop me from doing what I need to do.",
    "I have these sorts of pains most of the time.",
    "These pains are so bad they force me to stop what I am doing."
];

let ids30_q24_responses = [
    "I don't have any of these symptoms: heart pounding fast, blurred vision, sweating, hot and cold flashes, chest pain, heart turning over in my chest, ringing in my ears, or shaking.",
    "I have some of these symptoms but they are mild and are present only sometimes.",
    "I have several of these symptoms and they bother me quite a bit.",
    "I have several of these symptoms and when they occur I have to stop doing whatever I am doing."
];

let ids30_q25_responses = [
    "I have no spells of panic or specific fears (phobia) (such as animals or heights).",
    "I have mild panic episodes or fears that do not usually change my behavior or stop me from functioning.",
    `I have significant panic episodes or fears that force me to change my behavior but do <u>not</u> stop me functioning.`,
    "I have panic episodes at least once a week or severe fears that stop me from carrying on my daily activities."
];

let ids30_q26_responses = [
    "There is no change in my usual bowel habits.",
    "I have intermittent constipation or diarrhea which is mild.",
    "I have diarrhea or constipation most of the time but it does not interfere with my day-to-day functioning.",
    "I have constipation or diarrhea for which I take medicine or which interferes with my day-to-day activities."
];

let ids30_q27_responses = [
    "I have not felt easily rejected, slighted, criticized or hurt by others at all.",
    "I have occasionally felt rejected, slighted, criticized or hurt by others.",
    "I have often felt rejected, slighted, criticized or hurt by others, but these feelings have had only slight effects on my relationships or work.",
    "I have often felt rejected, slighted, criticized or hurt by others and these feelings have impaired my relationships and work."
];

let ids30_q28_responses = [
    "I have not experienced the physical sensation of feeling weighted down and without physical energy.",
    "I have occasionally experienced periods of feeling physically weighted down and without physical energy, but without a negative effect on work, school, or activity level.",
    "I feel physically weighted down (without physical energy) more than half the time.",
    "I feel physically weighted down (without physical energy) most of the time, several hours per day, several days per week."
];

let ids30_responses = [ids30_q1_responses, ids30_q2_responses, ids30_q3_responses, ids30_q4_responses, ids30_q5_responses, ids30_q6_responses, ids30_q7_responses, ids30_q8_responses, ids30_q9_responses, ids30_q10_responses, ids30_q11_responses, ids30_q12_responses, ids30_q13_responses, ids30_q14_responses, ids30_q15_responses, ids30_q16_responses, ids30_q17_responses, ids30_q18_responses, ids30_q19_responses, ids30_q20_responses, ids30_q21_responses, ids30_q22_responses, ids30_q23_responses, ids30_q24_responses, ids30_q25_responses, ids30_q26_responses, ids30_q27_responses, ids30_q28_responses];

let ids30_question_array = []

q = 0
for (let ids30_q of ids30_qs) {
    q += 1
    let q_string = q.toString() + ". "
    let tmp_json = {
        prompt: q_string + ids30_qs[q - 1],
        name: 'ids30_q' + q.toString(),
        options: ids30_responses[q - 1],
        required: false
    }
    ids30_question_array.push(tmp_json)
}


