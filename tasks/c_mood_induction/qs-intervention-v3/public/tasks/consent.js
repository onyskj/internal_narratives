var base_rate = '&#163;8.21/hour';
var max_rate = '&#163;9.21/hour';
var consent_content = `
<div id="consentmine">
    <h2 >Online studies in learning, decision-making and cognition: Information and consent</h2>
    <h3 id="study_subtitle">` + study_subname + `</h3>
    <p><b>Who is conducting this research study?</b></p>
    <p>
        This research is being conducted by the Division of Psychiatry and the Max Planck UCL Centre for Computational
        Psychiatry
        and Ageing Research at University College London, London, UK. The lead researchers for this project is
        <a href="mailto:q.huys@ucl.ac.uk">Dr Quentin Huys</a>. This study has been approved by the UCL Research Ethics
        Committee
        (project ID number 16639/001) and is funded by the Max Planck Society, the Masason Foundation and the UCL
        Institute of Mental Health.
    </p>

    <p><b>What is the purpose of this study?</b></p>
    <p>
        We are interested in how the adult brain controls learning and decision-making. This research aims to provide
        insights into how the healthy brain works to help us understand the causes of a number of different medical
        conditions.
    </p>

    <p><b>Who can participate in the study?</b></p>
<!--    <p>Please confirm whether or not you meet the eligibility criteria.</p>-->
<!--        <div style="display: inline; padding-left:20px">-->
<!--  <label for="yes_no_radio">You must be 18 or over to participate in this study.</label>-->
<!--&lt;!&ndash;    <p>&ndash;&gt;-->
<!--<br>-->
<!--    <input style="margin-top: 10px; margin-left:25px", type="radio", name="yes_no", required, id="age_radio">Yes</input>-->
<!--&lt;!&ndash;    </p>&ndash;&gt;-->
<!--&lt;!&ndash;    <p>&ndash;&gt;-->
<!--    <input type="radio" name="yes_no" required>No</input>-->
<!--&lt;!&ndash;    </p>&ndash;&gt;-->
<!--    </div>-->

    <p>
        You must be 18 or over to participate in this study.

        <p><b>What will happen to me if I take part?</b></p>
<!--        <p>You will play one or more online computer games, which will last approximately ` + dur_experiment + ` minutes.</p>-->
            <p>You will receive between ` + base_rate + ` and ` + max_rate + ` for helping us.</p>
<!--            The amount can vary with the decisions you make in the games.-->
<!--        </p>-->
        <p>You will be asked some questions about yourself, your feelings, background, attitudes and behaviour in your everyday life, which will last approximately ` + dur_experiment + ` minutes.</p>
        <p>
            Remember, you are free to withdraw at any time without giving a reason.
        </p>

        <p><b>What are the possible disadvantages and risks of taking part?</b></p>
        <p>
            The task you will complete does not pose any known risks.
        </p>
        <p>
            You will be asked to answer some questions about mood and feelings, and we will provide information about ways to seek help should you feel affected by the issues raised by these questions.
        </p>
<!--        <p class="check_maybe">-->
<!--            Moreover, some aspects of the study may contain descriptions of characters feeling bad about themselves-->
<!--        </p>-->

        <p><b>What are the possible benefits of taking part?</b></p>
        <p>
            While there are no immediate benefits to taking part, your participation in this research will help us
            understand how people make decisions and this could have benefits for our understanding of mental health
            problems.
        </p>

        <p><b>Complaints</b></p>
        <p>
            If you wish to complain or have any concerns about any aspect of the way you have been approached or treated
            by members of staff, then the research UCL complaints mechanisms are available to you. In the first
            instance,
            please talk to the <a href="mailto:q.huys@ucl.ac.uk">researcher</a> or the chief investigator
            (<a href="mailto:q.huys@ucl.ac.uk">Dr Quentin Huys</a>) about your
            complaint. If you feel that the complaint has not been resolved satisfactorily, please contact the chair of
            the <a href="mailto:ethics@ucl.ac.uk">UCL Research Ethics Committee</a>.

            If you are concerned about how your personal data are being processed please contact the data controller
            who is <a href="mailto:data-protection@ucl.ac.uk">UCL</a>.
            If you remain unsatisfied, you may wish to contact the Information Commissioner Office (ICO).
            Contact details, and details of data subject rights, are available on the
            <a href="https://ico.org.uk/for-organisations/data-protection-reform/overview-of-the-gdpr/individuals-rights">ICO
                website</a>.
        </p>

        <p><b>What about my data?</b></p>

        <p> This local privacy notice sets out the information that applies to this
            particular study. Further information on how UCL uses participant information
            can be found in our general privacy notice. For participants in research
            studies, click <a
                href="https://www.ucl.ac.uk/legal-services/privacy/ucl-general-research-participant-privacy-notice">here</a>.
            The information that is required to be provided to participants under data
            protection legislation (GDPR and DPA 2018) is provided across both the local and
            general privacy notices.</p>

        <p>To help future research and make the best use of the research data you have given us (such as answers to
            questionnaires) we may keep your research data indefinitely and share these. The data we collect will
            be shared and held as follows:
            <ul>
                <li>In publications, your data will be anonymised, so you cannot be identified.</li>
                <li>In public databases, your data will be anonymised or pseudonymised (your personal details
                will be removed and a code used e.g. 00001232, instead of your User ID).
                </li>
            </ul>
        </p>

        <p> Personal data is any information that could be used to identify you, such as
            your User ID. When we collect your data, your User ID will be replaced with a
            non-identifiable random ID number. No personally identifying data will be stored </p>

        <p>The legal basis used to process your personal data will be the provision of public task
        (this means that the research you are taking part in is deemed to be in the public interest).
        We will follow the UCL and legal guidelines to safeguard your data.</p>
        <p>If there are any queries or concerns please do not hesitate to contact <a href="mailto:q.huys@ucl.ac.uk">Dr
                Quentin Huys</a>. </p>

        <p><b>If you are happy to proceed please read the statement below and click the boxes to show that you
            consent to this study proceeding</b></p>

    </p>
    <label className="container">
        <input type="checkbox" id="consent_checkbox1">
            I confirm I am over 18 years old
            <span className="checkmark"></span>
    </label>
    <br> <br>

        <label className="container">
            <input type="checkbox" id="consent_checkbox2">
                I have read the information above, and understand what the study involves.
                <span className="checkmark"></span>
        </label> <br><br>

        <label className="container">
            <input type="checkbox" id="consent_checkbox3">
                I understand that my anonymised/pseudonymised personal data can be shared with others
                for future research, shared in public databases and in scientific reports.
                <span className="checkmark"></span> <br><br>
        </label>

        <label className="container">
            <input type="checkbox" id="consent_checkbox4">
                I understand that I am free to withdraw from this study at any time without
                giving a reason and this will not affect my future medical care or legal rights.
                <span className="checkmark"></span> <br><br>
        </label>

        <label className="container">
            <input type="checkbox" id="consent_checkbox5">
                I understand the potential benefits and risks of participating, the support available
                to me should I become distressed during the research, and who to contact if I wish to lodge a complaint.
                <span className="checkmark"></span> <br><br>
        </label>

        <label className="container">
            <input type="checkbox" id="consent_checkbox6">
                I understand the inclusion and exclusion criteria in the Information Sheet.
                I confirm that I do not fall under the exclusion criteria.
                <span className="checkmark"></span> <br><br>
        </label>

        <label className="container">
            <input type="checkbox" id="consent_checkbox7">
                I agree that the research project named above has been explained to me to my
                satisfaction and I agree to take part in this study
                <span className="checkmark"></span> <br><br>
        </label>

        <br>
            <button type="button" id="confirmButton" className="submit_button" >Continue</button>
            <br><br>
</div>
`;
