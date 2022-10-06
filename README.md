# FocusED

Application to detect attention level of the student attending online classes.

solution for this problem is modularized into two modules video and sound processing engine and attention reporting & analysis engine.​

Video and Sound Processing Engine :​

a. Video Processing​

   1. Learners are monitored through webcam.​
   2. Open Gaze, Open Pose & Head Pose are tracked to evaluate attention of learners.​
   3. The face is tracked and various positions are estimated using pre-trained facial landmarks. ​

b. Sound Processing​

  1. Proportion of two-way communication between learner and instructor .​
  2. Based on learners voice , interaction between learner and instructor is measured.​
  3. This is done using CNN based audio segmentation toolkit.​
