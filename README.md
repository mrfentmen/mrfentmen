# CAPABILITY TEST (temporary)

**1. ANIMATED GIF**
<img src="https://raw.githubusercontent.com/mrfentmen/mrfentmen/main/test.gif" width="240">

**2. SVG + SMIL**
<img src="https://raw.githubusercontent.com/mrfentmen/mrfentmen/main/cursor.svg" width="11" height="18">

**3. HTML &lt;video&gt; TAG**
<video src="https://raw.githubusercontent.com/mrfentmen/mrfentmen/main/test.mp4" width="240" autoplay loop muted></video>

**4. BARE VIDEO LINK**
https://raw.githubusercontent.com/mrfentmen/mrfentmen/main/test.mp4

**5. CSS**
<style>
@keyframes pul { 0%,100% { opacity:1 } 50% { opacity:0.15 } }
#csstest { color:#ff0000; font-weight:bold; animation: pul 1s infinite; }
</style>
<div id="csstest">CSS-MARKER</div>

**6. JS**
<div id="jstest">JS-MARKER-UNCHANGED</div>
<script>document.getElementById('jstest').textContent = 'JS-EXECUTED';</script>

**7. RELATIVE PATH**
<img src="cursor.svg" width="11" height="18">