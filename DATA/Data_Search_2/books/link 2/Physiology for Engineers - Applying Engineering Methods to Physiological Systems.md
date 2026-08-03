# Physiology for Engineers: Applying Engineering Methods to Physiological Systems

> **Source file:** `phs(30).pdf`  
> **Source URL:** https://github.com/manjunath5496/Physiology-Books/blob/master/phs%2830%29.pdf  
> **Pages:** 176  
> **Converted:** 2026-07-27 06:29 UTC  
> **Converter:** pdftotext (poppler/xpdf) 4.06 — text extracted page by page

---


<!-- ===== Page 1 ===== -->

Biosystems & Biorobotics
Michael Chappell Stephen Payne
Physiology for Engineers
Applying Engineering Methods to Physiological Systems


<!-- ===== Page 2 ===== -->

Biosystems & Biorobotics
Volume 13
Series editor
Eugenio Guglielmelli, Campus Bio-Medico University of Rome, Rome, Italy e-mail: e.guglielmelli@unicampus.it
Editorial Board
Dino Accoto, Campus Bio-Medico University of Rome, Rome, Italy Sunil Agrawal, University of Delaware, Newark, DE, USA Fabio Babiloni, Sapienza University of Rome, Rome, Italy Jose M. Carmena, University of California, Berkeley, CA, USA Maria Chiara Carrozza, Scuola Superiore Sant’Anna, Pisa, Italy Paolo Dario, Scuola Superiore Sant’Anna, Pisa, Italy Arturo Forner-Cordero, University of Sao Paolo, São Paulo, Brazil Masakatsu G. Fujie, Waseda University, Tokyo, Japan Nicolas Garcia, Miguel Hernández University of Elche, Elche, Spain Neville Hogan, Massachusetts Institute of Technology, Cambridge, MA, USA Hermano Igo Krebs, Massachusetts Institute of Technology, Cambridge, MA, USA Dirk Lefeber, Universiteit Brussel, Brussels, Belgium Rui Loureiro, Middlesex University, London, UK Marko Munih, University of Ljubljana, Ljubljana, Slovenia Paolo M. Rossini, University Cattolica del Sacro Cuore, Rome, Italy Atsuo Takanishi, Waseda University, Tokyo, Japan Russell H. Taylor, The Johns Hopkins University, Baltimore, MA, USA David A. Weitz, Harvard University, Cambridge, MA, USA Loredana Zollo, Campus Bio-Medico University of Rome, Rome, Italy


<!-- ===== Page 3 ===== -->

Aims & Scope
Biosystems & Biorobotics publishes the latest research developments in three main areas: 1) understanding biological systems from a bioengineering point of view, i.e. the study of biosystems by exploiting engineering methods and tools to unveil their functioning principles and unrivalled performance; 2) design and development of biologically inspired machines and systems to be used for different purposes and in a variety of application contexts. The series welcomes contributions on novel design approaches, methods and tools as well as case studies on speciﬁc bioinspired systems; 3) design and developments of nano-, micro-, macrodevices and systems for biomedical applications, i.e. technologies that can improve modern healthcare and welfare by enabling novel solutions for prevention, diagnosis, surgery, prosthetics, rehabilitation and independent living.
On one side, the series focuses on recent methods and technologies which allow multiscale, multi-physics, high-resolution analysis and modeling of biological systems. A special emphasis on this side is given to the use of mechatronic and robotic systems as a tool for basic research in biology. On the other side, the series authoritatively reports on current theoretical and experimental challenges and developments related to the “biomechatronic” design of novel biorobotic machines. A special emphasis on this side is given to human-machine interaction and interfacing, and also to the ethical and social implications of this emerging research area, as key challenges for the acceptability and sustainability of biorobotics technology.
The main target of the series are engineers interested in biology and medicine, and speciﬁcally bioengineers and bioroboticists. Volume published in the series comprise monographs, edited volumes, lecture notes, as well as selected conference proceedings and PhD theses. The series also publishes books purposely devoted to support education in bioengineering, biomedical engineering, biomechatronics and biorobotics at graduate and post-graduate levels.
About the Cover
The cover of the book series Biosystems & Biorobotics features a robotic hand prosthesis. This looks like a natural hand and is ready to be implanted on a human amputee to help them recover their physical capabilities. This picture was chosen to represent a variety of concepts and disciplines: from the understanding of biological systems to biomechatronics, bioinspiration and biomimetics; and from the concept of human-robot and human-machine interaction to the use of robots and, more generally, of engineering techniques for biological research and in healthcare. The picture also points to the social impact of bioengineering research and to its potential for improving human health and the quality of life of all individuals, including those with special needs. The picture was taken during the LIFEHAND experimental trials run at Università Campus Bio-Medico of Rome (Italy) in 2008. The LIFEHAND project tested the ability of an amputee patient to control the Cyberhand, a robotic prosthesis developed at Scuola Superiore Sant’Anna in Pisa (Italy), using the tf-LIFE electrodes developed at the Fraunhofer Institute for Biomedical Engineering (IBMT, Germany), which were implanted in the patient’s arm. The implanted tf-LIFE electrodes were shown to enable bidirectional communication (from brain to hand and vice versa) between the brain and the Cyberhand. As a result, the patient was able to control complex movements of the prosthesis, while receiving sensory feedback in the form of direct neurostimulation. For more information please visit http://www.biorobotics.it or contact the Series Editor.
More information about this series at http://www.springer.com/series/10421


<!-- ===== Page 4 ===== -->

Michael Chappell • Stephen Payne
Physiology for Engineers
Applying Engineering Methods to Physiological Systems
123


<!-- ===== Page 5 ===== -->

Michael Chappell Department of Engineering Science University of Oxford Oxford UK

Stephen Payne Department of Engineering Science University of Oxford Oxford UK

ISSN 2195-3562 Biosystems & Biorobotics ISBN 978-3-319-26195-9 DOI 10.1007/978-3-319-26197-3

ISSN 2195-3570 (electronic) ISBN 978-3-319-26197-3 (eBook)

Library of Congress Control Number: 2015955884

Springer Cham Heidelberg New York Dordrecht London © Springer International Publishing Switzerland 2016 This work is subject to copyright. All rights are reserved by the Publisher, whether the whole or part of the material is concerned, speciﬁcally the rights of translation, reprinting, reuse of illustrations, recitation, broadcasting, reproduction on microﬁlms or in any other physical way, and transmission or information storage and retrieval, electronic adaptation, computer software, or by similar or dissimilar methodology now known or hereafter developed. The use of general descriptive names, registered names, trademarks, service marks, etc. in this publication does not imply, even in the absence of a speciﬁc statement, that such names are exempt from the relevant protective laws and regulations and therefore free for general use. The publisher, the authors and the editors are safe to assume that the advice and information in this book are believed to be true and accurate at the date of publication. Neither the publisher nor the authors or the editors give a warranty, express or implied, with respect to the material contained herein or for any errors or omissions that may have been made.

Printed on acid-free paper

Springer International Publishing AG Switzerland is part of Springer Science+Business Media (www.springer.com)


<!-- ===== Page 6 ===== -->

To Angela Chappell BSc (Hons) aka Mum —Michael Chappell

To Alan

—Stephen Payne


<!-- ===== Page 7 ===== -->

Preface
As its name indicates, this short book is intended to give students in any branch of engineering an introduction to human physiology and how it can be approached by those with an engineering background. It will also provide an introduction for students in other physical science subjects to the approaches that can be adopted in understanding and modelling human physiology. We hope that it will provide a starting point for both students and nonstudents to explore what is fascinating about human physiology (which simply means the study of nature).
This book was written particularly with those wanting to enter the ﬁeld of biomedical engineering in mind. As biomedical engineers ourselves, we often get asked what biomedical engineering actually is and what its purpose is. Neither of us set out to train as biomedical engineers (we did our ﬁnal year undergraduate projects on land mines and jet engines), but we both ended up in this area because it opened up so many interesting problems to work on. If engineering is the “appliance of science”1, then biomedical engineering is the appliance of engineering to medicine. The whole point is to help to solve problems that will one day improve health care.
Let us give you an example, directly related to our research. How can we best decide what treatment to give someone coming into a hospital with a stroke? Doctors will do brain imaging, mostly likely a CT scan, or in some hospitals, an MRI scan. How does the doctor then decide what best to do? Stroke is essentially a plumbing problem and comes in two forms: Blockage—an ischaemic stroke arises when a vessel feeding part of the brain gets blocked. Leakage—an haemorrhagic stroke arises when blood is leaking into the brain from a broken blood vessel. Both forms of stroke need urgent attention and the solutions seem simple: remove a blockage or stop a leak.
1Our thanks to Zanussi.
vii


<!-- ===== Page 8 ===== -->

viii

Preface

However, there are lots of complications to this. For example, in an ischaemic stroke, should the doctor operate and try to pull the clot out or should he/she try to dissolve the clot by injecting a blood thinning drug? Often the person is very elderly with many other illnesses and so an operation is not a good idea; likewise, the blood thinner may result in a blood vessel bursting and a haemorrhage (leak) elsewhere in the brain.
The doctor has to make a rapid treatment decision and does so based on a lot of experience. What we can do as biomedical engineers in this context is to help in the decision-making process by providing (1) the best and most useful information from the brain imaging and (2) the best predictions of outcome for various treatment decisions. By doing this and providing the doctor with the most useful information to make a well-informed decision, biomedical engineers can help to get the best outcomes for these patients. This will not only help to save lives, but also help to reduce the levels of disability that stroke patients have to live with when they leave the hospital. Even a small improvement in the outcome of a stroke patient can make the difference between living at home and living in a home, or between independent and dependent living.
The tools we have to do this are both physical (imaging devices) and mathematical (systems of equations), things that engineers excel in. This needs to be matched with an understanding of the problem, and this requires the knowledge of not only how the body works, but also how our tools apply to that physiology. Hence, this book is an attempt to guide the reader in bridging what appears to be a divide between physical and biomedical sciences.
There are a number of things to note about the book:
1. It is introductory: deliberately, we are covering a wide range of material at a high level. There are many other very good textbooks that will take you into much greater detail, but the purpose here is simply to give you an introduction to physiology from an engineering viewpoint. We also do not attempt to cover all of physiology, rather we have chosen what we hope are a selection of illustrative and interesting examples.
2. It is quantitative: the focus is very much on turning the underlying physiology into mathematics so that a system, whether it is a single cell or the whole brain, can be modelled and interpreted using engineering techniques.
3. It is concerned with clinical measurements: since we can only know about what we can measure, throughout the book we have detailed the most common clinical measurement techniques that can be used to gain information about the topics presented here.
At the end of the book, we hope that you will have gained some insight into human physiology and how we can express this mathematically and measure it, using core engineering techniques. You will then hopefully also be better equipped to apply the same principles and techniques to other aspects of physiology that we have not covered here.
The book starts with the cell, which is the fundamental unit of the body. We will examine its structure, its function and how it operates: in particular we will examine


<!-- ===== Page 9 ===== -->

Preface

ix

the generation of the action potential and how this is transmitted between cells. We will then gradually move to larger scales and look at various systems in the body, primarily the cardiovascular, respiratory and nervous systems.
We have included exercises, but instead of including them all at the end of each chapter, we have deliberately inserted them in the text at the most appropriate point. Many of the examples require you to explore a result that has been stated or to work through a similar example. It is not necessary to do the examples as you read through the book (and they are clearly highlighted), but we hope that they will be helpful in reinforcing the ideas presented, and in particular giving you experience in applying engineering techniques to physiological problems. There are brief solutions given at the end of the book.
This book does draw on a very wide range of engineering knowledge, which we appreciate that you will not all have. For some of you, phasor analysis will be a mystery; for others, elasticity theory will be incomprehensible. We have tried to keep the level of knowledge required to a minimum, but since this is not a course in basic engineering, there may be some parts that you will not understand. We hope that at least you will get some insight into what is going on, even if you do not follow all of the equations and mathematics in every chapter.
As academics, we have taught a similar course for nearly ten years to undergraduate and graduate students at the University of Oxford. We have, like all academics, learnt a great deal ourselves over this time, and we take this opportunity to thank the students who have attended our course in its various different incarnations. In all of this, we have been able to draw on our experience teaching our students, to the book’s great beneﬁt; however, any errors that remain are naturally entirely our fault.


<!-- ===== Page 10 ===== -->

Contents
1 Cell Structure and Biochemical Reactions . . . . . . . . . . . . . . . . . . 1 1.1 Cell Structure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1 1.2 Cell Chemicals . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2 1.2.1 Proteins . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3 1.2.2 ATP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3 1.2.3 DNA/RNA . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4 1.3 Reaction Equations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5 1.3.1 Mass Action Kinetics . . . . . . . . . . . . . . . . . . . . . . . 7 1.3.2 Enzyme Kinetics . . . . . . . . . . . . . . . . . . . . . . . . . . . 9 1.3.3 Enzyme Cooperativity . . . . . . . . . . . . . . . . . . . . . . . 13 1.3.4 Enzyme Inhibition. . . . . . . . . . . . . . . . . . . . . . . . . . 15 1.4 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
2 Cellular Homeostasis and Membrane Potential. . . . . . . . . . . . . . . 19 2.1 Membrane Structure and Composition . . . . . . . . . . . . . . . . . . 19 2.2 Osmotic Balance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21 2.3 Conservation of Charge . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25 2.4 Equilibrium Potential . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26 2.5 A Simple Cell Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27 2.6 Ion Pumps . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28 2.7 Membrane Potential . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29 2.8 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
3 The Action Potential . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33 3.1 Na+/K+ Action Potential. . . . . . . . . . . . . . . . . . . . . . . . . . . . 33 3.2 Ca2+ Contribution . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36 3.3 Hodgkin-Huxley Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36 3.4 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41
xi


<!-- ===== Page 11 ===== -->

xii

Contents

4 Cellular Transport and Communication. . . . . . . . . . . . . . . . . . . . 43 4.1 Transport . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43 4.1.1 Passive Transport . . . . . . . . . . . . . . . . . . . . . . . . . . 43 4.1.2 Carrier-Mediated Transport. . . . . . . . . . . . . . . . . . . . 45 4.1.3 Active Transport . . . . . . . . . . . . . . . . . . . . . . . . . . . 46 4.2 Cellular Communication . . . . . . . . . . . . . . . . . . . . . . . . . . . 48 4.3 Synapses . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48 4.3.1 Electrical Synapses . . . . . . . . . . . . . . . . . . . . . . . . . 49 4.3.2 Chemical Synapses . . . . . . . . . . . . . . . . . . . . . . . . . 49 4.4 Action Potential Propagation . . . . . . . . . . . . . . . . . . . . . . . . 51 4.5 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54
5 Pharmacokinetics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55 5.1 ADME Principles . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55 5.2 Compartmental Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56 5.2.1 One Compartment Model . . . . . . . . . . . . . . . . . . . . . 56 5.2.2 Absorption Compartment . . . . . . . . . . . . . . . . . . . . . 59 5.2.3 Peripheral Compartment. . . . . . . . . . . . . . . . . . . . . . 61 5.2.4 Multi Compartment Models . . . . . . . . . . . . . . . . . . . 61 5.2.5 Non-linear Models . . . . . . . . . . . . . . . . . . . . . . . . . 62 5.3 Tracer Kinetics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63 5.4 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66
6 Tissue Mechanics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67 6.1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67 6.2 Stress-Strain Relationships . . . . . . . . . . . . . . . . . . . . . . . . . . 67 6.2.1 Linear Material . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69 6.2.2 Non-linear Material . . . . . . . . . . . . . . . . . . . . . . . . . 70 6.3 Coupled Cell-Tissue Model . . . . . . . . . . . . . . . . . . . . . . . . . 71 6.4 Coupled Fluid-Tissue Model . . . . . . . . . . . . . . . . . . . . . . . . 73 6.5 Coupled Blood Vessel-Tissue Model . . . . . . . . . . . . . . . . . . . 75 6.5.1 Plane Stress . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76 6.5.2 Plane Strain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77 6.6 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79
7 Cardiovascular System I: The Heart . . . . . . . . . . . . . . . . . . . . . . 81 7.1 Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81 7.2 Structure and Operation of the Heart . . . . . . . . . . . . . . . . . . . 83 7.3 Measurement of Cardiac Output . . . . . . . . . . . . . . . . . . . . . . 85


<!-- ===== Page 12 ===== -->

Contents

xiii

7.4 Electrical Activity of the Heart . . . . . . . . . . . . . . . . . . . . . . . 86 7.4.1 The Action Potential . . . . . . . . . . . . . . . . . . . . . . . . 87 7.4.2 Pacemaker Potential . . . . . . . . . . . . . . . . . . . . . . . . 88 7.4.3 Cardiac Cycle . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 89 7.4.4 Introduction to Electrocardiography . . . . . . . . . . . . . . 91
7.5 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 95
8 Cardiovascular System II: The Vasculature . . . . . . . . . . . . . . . . . 97 8.1 Anatomy of the Vascular System . . . . . . . . . . . . . . . . . . . . . 97 8.2 Blood . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99 8.3 Haemodynamics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 100 8.4 Blood Pressure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105 8.4.1 Long-Term Measurement Techniques . . . . . . . . . . . . 108 8.4.2 Short-Term Measurement Techniques . . . . . . . . . . . . 109 8.5 Measurement of Blood Supply . . . . . . . . . . . . . . . . . . . . . . . 109 8.5.1 Blood Flow . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110 8.5.2 Perfusion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 110 8.6 Control of Blood Flow . . . . . . . . . . . . . . . . . . . . . . . . . . . . 111 8.6.1 Individual Vessels . . . . . . . . . . . . . . . . . . . . . . . . . . 111 8.6.2 Individual Body Organs . . . . . . . . . . . . . . . . . . . . . . 112 8.6.3 Whole Body . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114 8.7 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
9 The Respiratory System . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 117 9.1 The Lungs and Pulmonary Circulation . . . . . . . . . . . . . . . . . . 117 9.1.1 Breathing . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118 9.1.2 Respiration Rate . . . . . . . . . . . . . . . . . . . . . . . . . . . 118 9.2 Gas Transport. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120 9.2.1 Inert Gases . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120 9.2.2 Carbon Dioxide . . . . . . . . . . . . . . . . . . . . . . . . . . . 122 9.2.3 Oxygen . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 123 9.2.4 Tissue Gas Delivery . . . . . . . . . . . . . . . . . . . . . . . . 123 9.2.5 Blood Oxygenation . . . . . . . . . . . . . . . . . . . . . . . . . 126 9.2.6 Control of Acid-Base Balance. . . . . . . . . . . . . . . . . . 127 9.3 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
10 The Central Nervous System . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129 10.1 Neurons . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 129 10.2 Autonomic Nervous System . . . . . . . . . . . . . . . . . . . . . . . . . 131 10.2.1 Autonomic Control of the Heart . . . . . . . . . . . . . . . . 131 10.2.2 Cardiac Efferents . . . . . . . . . . . . . . . . . . . . . . . . . . 132 10.2.3 Cardiac Afferents . . . . . . . . . . . . . . . . . . . . . . . . . . 133


<!-- ===== Page 13 ===== -->

xiv

Contents

10.3 Somatic Nervous System . . . . . . . . . . . . . . . . . . . . . . . . . . . 134 10.3.1 Temporal and Spatial Summation of Synaptic Potentials . . . . . . . . . . . . . . . . . . . . . . . 135 10.3.2 Excitatory and Inhibitory Synapses . . . . . . . . . . . . . . 136 10.3.3 The Brain. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 137 10.3.4 Function: Introduction to EEG and FMRI . . . . . . . . . 138
10.4 Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 139

Answers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

Further Reading . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 167


<!-- ===== Page 14 ===== -->

Chapter 1
Cell Structure and Biochemical Reactions

1.1 Cell Structure
We start by examining the cell, since it is the fundamental unit of living matter. There are brain cells, heart cells, liver cells and so on, in every part of the body. Each of these cells has a speciﬁc function and purpose. Despite this all cells have some characteristics in common, as shown schematically in Fig. 1.1. There are four main components. Cells have an outer layer, called the membrane, which acts as the boundary between the inside and outside of the cell. We will examine this in more detail in the next chapter.
Inside the cell, there is a nucleus that contains the cell’s DNA, i.e. the genetic code that determines what the cell does, and many small structures that carry out the operations for the cell, termed organelles. Unsurprisingly there are lots of these, each with particular roles. They include ribosomes, lysosomes and mitochondria, where many of the reactions that produce energy take place. The rest of the cell is occupied by a gel-like ﬂuid, called the cytosol, that contains ions and other substances and that surrounds the other internal elements. The cytosol and the organelles together are termed the cytoplasm. We will examine a number of these elements, primarily the membrane and the cytoplasm, in more detail later on.
More formally, we classify a cell as the smallest independently viable unit of a living organism. It is therefore self-contained and self-maintaining. The smallest organism is made up of just one cell, whereas the largest are made up of billions of cells. All cells can reproduce by cell division and metabolise, which means that they take in and process raw materials and release the by-products of metabolism. Cells also respond to both external and internal stimuli, for example temperature and pH.

© Springer International Publishing Switzerland 2016

1

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_1


<!-- ===== Page 15 ===== -->

2

1 Cell Structure and Biochemical Reactions

Fig. 1.1 Structure of the cell (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
1.2 Cell Chemicals
Before examining the cell in detail, we will look at the different types of chemicals found in the body and their roles, such that when we consider the functions of the cell, it will be easier to understand what it is doing. Note that we will only look at a few of the most important substances found within a cell.
The important chemicals within the body can be divided into two categories: inorganic and organic. The difference is very simply that organic compounds always contain carbon, whereas most inorganic compounds do not contain carbon.
The main inorganic substances are:
1. Water, which acts as a solvent, a biochemical reactant, a regulator of body temperature and a lubricant;
2. Electrolytes, which balance osmotic pressure and biochemical reactants; 3. Acids and bases, which act to balance pH.
The primary organic substances are:
1. Carbohydrates; 2. Lipids; 3. Proteins; 4. Nucleic acids (including DNA and RNA); 5. Adenosine triphosphate (ATP).


<!-- ===== Page 16 ===== -->

1.2 Cell Chemicals

3

Carbohydrates, proteins and nucleic acids are all necessary for life to function. Cells are made up of just three substances: water; inorganic ions; and organic molecules. Water makes up around 70 % of cell mass, with most of the rest being organic molecules: inorganic ions make up only a few percent. The inorganic ions include sodium (Na+), potassium (K+), calcium (Ca2+), chloride (Cl−) and bicarbonate (HCO3−). The plus and minus signs are used to tell us that the ions are positively or negatively charged: this will be very important when we consider how the cell behaves later on. We don’t always explicitly write the plus or minus signs though, since only a handful of ions are involved and we tend to know what their charges are.

1.2.1 Proteins
There are many types of proteins and they perform lots of roles within the body, including:
1. Structural (coverings and support); 2. Regulatory (hormones, control of metabolism); 3. Contractile (muscles); 4. Immunological (antibodies, immune system); 5. Transport (movement of materials, haemoglobin for oxygen); 6. Catalytic (enzymes).
Proteins are large molecules made up of amino acids (of which there are around 20 in the human body): examples of proteins are insulin, haemoglobin and myosin. Insulin plays a key role in the regulation of blood sugar levels; haemoglobin is vital to the transport of oxygen around the body and myosin is used in muscle contraction.
Proteins differ between themselves in their order of amino acids, which is determined by their gene sequence; they are folded into speciﬁc three-dimensional shapes. The unique folded structure of a protein is often a very important determinant of its function. Proteins are formed, used and recycled with a lifespan that can vary from minutes to years. A schematic of the structure of haemoglobin, a typical protein, is shown in Fig. 1.2. The ﬁnal structure is made up of four sub-units, each of which is a highly folded and bonded version of the original chain of amino acids.

1.2.2 ATP
Adenosine triphosphate (ATP) is essentially the energy source for cells and acts like a battery. It is created by the conversion of glucose and oxygen into carbon dioxide, water and ATP:


<!-- ===== Page 17 ===== -->

4

1 Cell Structure and Biochemical Reactions

Fig. 1.2 Protein structure of haemoglobin (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)

C6H12O6 þ 6O2 ! 6CO2 þ 6H2O þ ATP

ð1:1Þ

This is why we breathe in oxygen and breathe out carbon dioxide: to convert glucose (a sugar) into an energy store that can be used for cells to function.
Figure 1.3 shows the three parts that make ATP molecules, with the third part comprising three phosphate groups (hence ‘triphosphate’). When the third, terminal, phosphate is released, energy is also liberated: ATP then becomes ADP (adenosine diphosphate), i.e. with only two phosphate groups. If the second phosphate is also released, to yield AMP (adenosine monophosphate), more energy is liberated. This energy is used to power many cellular processes, as we will see later.

1.2.3 DNA/RNA
Deoxyribonucleic acid (DNA for short) is the molecule that contains most of the genetic information that controls all of the processes that occur in the cell. As can be


<!-- ===== Page 18 ===== -->

1.2 Cell Chemicals

5

Fig. 1.3 Structure of ATP (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
seen in Fig. 1.4, there are two base pairs: adenine (A) with thymine (T), and guanine (G) with cytosine (C). These are connected to a sugar and a phosphate molecule, together called a nucleotide, which are arranged in the famous double helix structure shown in Fig. 1.4. The order of the bases encodes the information contained in each strand of DNA.
DNA is then organised into chromosomes: human cells have 23 pairs of chromosomes including the X and Y sex chromosomes. Chromosomes are sub-divided into genes, with each gene having its own function, instructing cells to make speciﬁc proteins. Ribonucleic acid (RNA) is the molecule that is used to convey genetic information by translating the information in a speciﬁc gene into a protein’s amino acid sequence: unlike DNA, RNA is single-stranded.
1.3 Reaction Equations
Now that we have discussed how a cell is constructed, it is time to consider how we analyse its behaviour. We do this analysis using reaction equations, which describe how one set of atoms and molecules (reactants) combine to form a different set of atoms and molecules (products).


<!-- ===== Page 19 ===== -->

6
Fig. 1.4 Structure of DNA (this ﬁgure is taken, without changes, from OpenStax College under license: http:// creativecommons.org/ licenses/by/3.0/)

1 Cell Structure and Biochemical Reactions

However, before we start to do this, we need to consider the correct use of units. Throughout this book, we will use the mole, which is formally deﬁned as the number of atoms found in 12 grams of 12C (6.022 × 1023 atoms), as the basic unit. Chemical equations are all based on the use of the mole, since it is a much more convenient means of describing quantities than simple weight or volume.
We said earlier that 70 % of the cell is water and so for many physiological elements, the molecules are not found in isolation, but in solution, primarily in water. We thus need a way to describe how much of the solute is present in the solution. The most common deﬁnition, although there are others, is called molarity: this is the number of moles of the solute per litre of solution. It thus has units of mol/l, which is normally written in shorthand as M. We will use this all the way through the remainder of this book unless stated otherwise. Since most physiological molarities are much less than 1 M, you should get used to seeing the abbreviation for milli-molar, which is written mM.


<!-- ===== Page 20 ===== -->

1.3 Reaction Equations

7

1.3.1 Mass Action Kinetics

Let’s start by writing down one of the very simplest reaction equations:

k
AþB!C

ð1:2Þ

k is termed the rate constant for this reaction, which simply takes two reactants, A and B, and converts them into one product C. The quantity of C increases dependent upon the quantities of both A and B, thus a simple model for rate of change of the concentration of the product with time (termed the reaction rate) is given by:

d½C ¼ k½A½B dt

ð1:3Þ

This is called the law of mass action and systems that obey this style of equation are said to be governed by mass action kinetics. The rate constant will depend upon the sizes and shapes of A and B; it also varies strongly with temperature (as well as with other factors such as pH).
Mass action kinetics are based on C being produced when A and B collide and combine, so-called elementary reactions. The rate constant is thus proportional to the number of collisions between A and B per unit time and the probability that the collision has enough energy.
Note that concentrations are usually denoted by square brackets, i.e. the concentration of A is [A]. However, for simplicity we will often use lower case letters to refer to chemical concentrations where we need to write many equations (see the next example below, where we do this to make writing the equations easier).
We should also note that Eq. (1.3) is not always true: for very high or very low concentrations, the rate of change is limited by other factors. Despite this, the equation is a good ﬁrst approximation and will enable us to analyse even quite complicated systems in a straightforward way.
If there are multiple moles on the left hand side of the reaction equation, then the reaction rate is proportional to the concentrations to the relevant powers, i.e. the reaction rate for the reaction:

k
A þ 2B ! C

ð1:4Þ

is:

dc ¼ kab2 dt

ð1:5Þ

Also, all reactions strictly speaking must be reversible to some extent, thus there are forward and reverse rate constants, which need not be the same:


<!-- ===== Page 21 ===== -->

8

1 Cell Structure and Biochemical Reactions

kþ
AþB  C
kÀ

ð1:6Þ

For this example, we can write down three equations, one for each of the chemical substances:

da ¼ kÀc À k þ ab dt db ¼ kÀc À k þ ab dt dc ¼ k þ ab À kÀc dt

ð1:7Þ ð1:8Þ ð1:9Þ

Although this now looks rather complicated, if we add the ﬁrst and third equations together, the rate of change of a + c is equal to zero. Integrating up this equation tells us that the sum of these two concentrations is a constant, which we deﬁne here as: a + c = ao, i.e. ao can be thought of as the initial amount of A before any was converted to C.
We can use the equilibrium condition in these equations. By setting the rates of change to zero in the three equations, we ﬁnd:

kÀ ¼ ab ¼ K kþ c

ð1:10Þ

where we use the over-bar to refer to the equilibrium or steady-state values of each substance. The ratio of the two rate constants, which we call K, is termed the equilibrium constant. This measures the relative preference for the substances to be in the combined, C, or separate, A + B, state. Note that we can deﬁne this either way up: we have chosen here to use the backwards rate divided by the forward rate, but we could just as easily have deﬁned it the other way.
This equation can be used to determine the equilibrium constant using the equilibrium values of the concentrations. The rule for determining the constant is to multiply all the reactant concentrations to the power of their coefﬁcients and divide by the product of the product concentrations, again each to the power of their coefﬁcients. The following two exercises will help you get some practice at this.

Exercise A A reaction takes place according to:
kþ
A þ 2B  C þ D
kÀ

ðA:1Þ


<!-- ===== Page 22 ===== -->

1.3 Reaction Equations

9

Write down the four reaction equations and show that the equilibrium constant is given by:

2
kÀ ab ¼
k þ cd

ðA:2Þ

Exercise B
A reaction takes place that turns reactants A and B into products D, E and F according to the following separate reaction steps:

kþ1
AþB  CþD
kÀ1

ðB:1Þ

kþ2
C  EþF
kÀ2

ðB:2Þ

a. Write down the reaction equations for A using Eq. B.1 and for C using Eq. B.2.
b. Assuming that both reactions are in equilibrium, show that the equilibrium constant for the whole reaction is given by:

K ¼ ab ¼ kÀ1 kÀ2 def k þ 1 k þ 2

ðB:3Þ

1.3.2 Enzyme Kinetics
Now that we have considered simple reaction equations and how to analyse them, we will look at one particular category of reaction that is very important: one where the reaction is catalysed by an enzyme. Enzymes are essentially substances that help other molecules called substrates change into products but which themselves are left unaffected by the reaction: they are sometimes known as catalysts.
One way in which enzymes work is by lowering the activation energy of the reaction, i.e. they make it easier to move from one state to another, as shown in Fig. 1.5. Activation energy is the transient energy required to proceed with a reaction and is often larger than the energy required or released by the reaction itself. For example, a reaction may require breaking of some atomic bonds before new bonds are formed. Thus to proceed along the reaction, moving from left to right in the ﬁgure, a large and temporary source of energy is required, giving the


<!-- ===== Page 23 ===== -->

10
Fig. 1.5 Enzymes and activation energy (this ﬁgure is taken, without changes, from OpenStax College under license: http:// creativecommons.org/ licenses/by/3.0/)

1 Cell Structure and Biochemical Reactions

characteristic ‘hill’ shown here. The enzyme lowers this ‘hill’, making it easier for the reaction to proceed.
Enzymes are particularly efﬁcient at speeding up biological reactions and are highly speciﬁc, thus allowing very precise control of the reaction speed. Remember that our simple model is that of an elementary reaction that depends upon the rate of collision of the reactants and the probability of the reaction having enough energy. A simple example of enzyme action would be a protein that ‘ﬁts’ a particular molecule in such a way that it causes a bond to be stressed making that bond more easily broken and thus reducing the activation energy, making the probability of reaction higher. Alternatively a protein might have ‘sites’ to which the species involved in the reaction bind, so that the enzyme increases the rate at which the species are brought together.
The ﬁrst model to consider enzyme reactions was proposed by Michaelis and Menten. The enzyme E converts the substrate S into the product P in two stages. S and E ﬁrst combine to give a complex C (sometimes written as ES), which then breaks down into E and P:

kþ1 kþ2
EþS  C !EþP
kÀ1

ð1:11Þ

In theory this second reaction can also work backwards, but normally P is continually removed, which prevents the reverse reaction from occurring, so we approximate it as a one way reaction. We can represent this process in diagrammatic form, as shown in Fig. 1.6, where the two substrates (in this case called S1 and S2) join together with the enzyme to form a product before being released from the enzyme.
We can write down the four differential equations in the same way as before for the four different substances, S, E, C and P:


<!-- ===== Page 24 ===== -->

1.3 Reaction Equations

11

Fig. 1.6 Stages in an enzyme reaction (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)

ds ¼ kÀ1c À k þ 1se dt

ð1:12Þ

de ¼ kÀ1c À k þ 1se þ k þ 2c dt

ð1:13Þ

dc ¼ k þ 1se À k þ 2c À kÀ1c dt

ð1:14Þ

dp ¼ k þ 2c dt

ð1:15Þ

Note that this set of equations is redundant: the second and third equations add to give zero, which means that the sum of E and C is constant over time and so we introduce a new constant, normally represented by e + c = eo.
There are two common approaches to analysing this system of equations: the
equilibrium approximation and the quasi-steady-state approximation. We will examine them both brieﬂy here.

1.3.2.1 Equilibrium Approximation

The ﬁrst method is the original one proposed by Michaelis and Menten and assumes that the substrate is always in equilibrium with the complex, i.e. the ﬁrst stage of the reaction is in equilibrium and hence ds=dt ¼ 0. The rate of formation of the product, termed the velocity of the reaction, is then given by:

V ¼ dp ¼ k þ 2c ¼ k þ 2eos

dt

Ks þ s

ð1:16Þ

where Ks ¼ kÀ1=k þ 1, similarly to before.


<!-- ===== Page 25 ===== -->

12
Fig. 1.7 Michaelis-Menten reaction behaviour (for Ks = 0.5 and Vmax = 1)

1 Cell Structure and Biochemical Reactions

At small substrate concentrations, the reaction rate is proportional to the amount of available enzyme and the amount of substrate: however, at large substrate concentrations, the rate is limited by the amount of enzyme present. The second reaction is thus termed rate limiting since the reaction velocity cannot increase beyond a certain value.
Equation (1.16) is often re-written in the form:

V ¼ Vmaxs Ks þ s

ð1:17Þ

where Vmax is so called because it is the maximum velocity with which the reaction can proceed. This equation is known as the Michaelis-Menten equation and is used widely in physiological modelling to mimic processes where there is a limited rate of reaction. It is shown in Fig. 1.7, where the asymptote and the initial slope are shown as straight lines: note that the square marks the point at which the reaction velocity reaches half of its maximum value (this is obviously when s ¼ Ks).

1.3.2.2 Quasi-Steady-State Approximation

The second approximation assumes that the rates of formation and the breakdown of the complex are equal, thus dc=dt ¼ 0. Solution of the remaining equations gives a very similar result to the previous reaction velocity:

V ¼ Vmaxs Km þ s

ð1:18Þ

where Km ¼ ðkÀ1 þ k2Þ=k þ 1. Clearly the two approximations give very similar results, and they are both of Michaelis-Menten form, but they are based on very different assumptions.


<!-- ===== Page 26 ===== -->

1.3 Reaction Equations

13

Exercise C
Derive the results shown in Eqs. (1.17) and (1.18). Explain why the quasi-steady-state reaction velocity is always smaller than the equilibrium reaction velocity.
Exercise D
Explain why plotting 1/V as a function of 1/s for a Michaelis-Menten reaction gives a straight line. Sketch this function and explain how the constants in this equation can be found from the intercepts with the two axes.
This model is very simple and is not normally an accurate reﬂection of the various stages of a true enzyme assisted reaction. A more detailed model was later proposed by Briggs and Haldane, where the complex has two phases (ES and EP). This has the same form as Eqs. 1.17 and 1.18, but again with a different constant. We can obviously extend the analysis to as complex a model as we wish (and we will look at some of these below), but the analysis does become increasingly laborious to perform. In practice, quite often a simple approximation is sufﬁcient to capture most of the behaviour of the system, especially if it is operating near either a linear or a saturated regime.

1.3.3 Enzyme Cooperativity

Some enzymes can bind more than one substrate molecule, such that the binding of one substrate molecule affects the binding of subsequent molecules. This is known as cooperativity and is involved in one of the most important bindings found in the human body: that of oxygen to haemoglobin in the blood. Although the analysis is quite complicated, the ﬁnal result is relatively simple: if n substrate molecules can bind to the enzyme, the rate of reaction is given by:

Vmax sn V¼ n n
K þs

ð1:19Þ

This is known as the Hill equation. It is frequently used as an approximation for reactions where the intermediate steps are not well known and is then derived from ﬁts to experimental data. The shape of the Hill equation for different values of n is shown in Fig. 1.8, illustrating how this can be used to ﬁt different shapes of curves derived from experimental data. In particular, note that the curve becomes much sharper for larger values of n (the asymptote is at 1, just as in the previous Figure).


<!-- ===== Page 27 ===== -->

14
Fig. 1.8 Hill equation reaction behaviour, for different values of n

1 Cell Structure and Biochemical Reactions

This is particularly true in the case of oxygen binding to haemoglobin, where the reaction equation:

kþ
Hb þ 4O2  HbðO2Þ4
kÀ

ð1:20Þ

turns out to imply a fraction ﬁlling of available haemoglobin sites, S, of:

½O2n

S¼ n

n

K þ ½O2

ð1:21Þ

with n = 4. In fact, a much better ﬁt to experimental data is found with n = 2.5, implying that the later sites prefer to ﬁll up if the early sites are already full. Precisely how this positive cooperativity occurs, however, is not yet completely understood. This example, which is known as the oxygen saturation curve and which is very important in respiration, as we will see in Chap. 9, provides a useful early illustration of a model that provides a good understanding of how the reaction processes occur, but where the result has to be adapted according to the real behaviour. The oxygen saturation curve is also affected by pH, temperature and CO2 levels, amongst other things.

Exercise E
a. Show that the Hill equation can be written as a straight line plot if the value of Vmax is known.
b. Sketch this function and explain how the intercepts with the two axes can be used to calculate the values of n and Km. Given the values in the table


<!-- ===== Page 28 ===== -->

1.3 Reaction Equations

15

below, calculate the values of n and Km, assuming that Vmax = 1 mM. Is the Hill equation a good ﬁt to this data set?

Substrate conc. (mM)

0.2 0.5 1.0 1.5 2.0 2.5 3.5 4.5

Reaction velocity (mM/s) 0.01 0.06 0.27 0.5 0.67 0.78 0.89 0.94

1.3.4 Enzyme Inhibition
In many cases, it is very important to have control over the reaction rate, so that it can be altered under different conditions, for example speeded up when demand for the product is greater, or slowed down when demand drops. An enzyme inhibitor is thus often used to reduce the rate of reaction, as explained below. There are two types that we will look at here: competitive and allosteric inhibitors.

1.3.4.1 Competitive Inhibitors

In this case, the inhibitor species combines with the enzyme to form a compound, which essentially removes some of the enzyme from the system, preventing it from forming the product: hence the idea of competition for the enzyme. The reactions are thus:

kþ1

kþ2

E þ S  C1 ! E þ P

kÀ1

ð1:22Þ

kþ3
E þ I  C2
kÀ3

ð1:23Þ

There are now six differential equations: ds ¼ kÀ1c1 À k þ 1se dt
de ¼ kÀ1c1 þ k þ 2c1 À k þ 1se þ kÀ3c2 À k þ 3ie dt
dc1 ¼ k þ 1se À ðk þ 2 þ kÀ1Þc1 dt
dp ¼ k þ 2c1 dt

ð1:24Þ ð1:25Þ ð1:26Þ ð1:27Þ


<!-- ===== Page 29 ===== -->

16

1 Cell Structure and Biochemical Reactions

di ¼ kÀ3c2 À k þ 3ie dt

ð1:28Þ

dc2 ¼ k þ 3ie À kÀ3c2 dt

ð1:29Þ

Thankfully, this isn’t as complicated as it looks. The normal assumption made in the analysis is that both the compounds are in quasi-steady-state. We can also see that if we add the differentials for the enzyme and the two compounds that they add up to zero (so these three variables always add up to a constant, which we will again call eo).
The rate of formation of the product is then found to be:

V ¼ dp ¼ k þ 2c1 ¼

Vmaxs

dt

Kmð1 þ i=KiÞ þ s

ð1:30Þ

where Ki ¼ kÀ3=k þ 3. Note that if i is set to zero, we get back to the original Michaelis-Menten equation, just as we would expect.

Exercise F
a. Derive the result in (1.30), given that dc1=dt ¼ 0 and dc2=dt ¼ 0 in quasi-steady-state, and that c1 þ c2 þ e ¼ eo.
b. Sketch the result for different values of inhibitor. Explain how the inhibitor affects the intercepts on the 1/V versus 1/s plot.

At this point, we will just note that the reaction equations can be re-written in schematic form (where we have omitted the rate constants for simplicity), as shown below.

This diagrammatic form can be very helpful in seeing how the reaction equations link together and understanding how substances ‘move’ around the system.


<!-- ===== Page 30 ===== -->

1.3 Reaction Equations

17

1.3.4.2 Allosteric Inhibitors

In this case the inhibitor binds to the enzyme in such a way as to prevent the product being formed. For example, the inhibitor might bind to a different site on the enzyme preventing the complex converting into the product. This can be modelled as the inhibitor binding to the complex, written in schematic form as shown below (note how we have moved to simply sketching the diagram to explain the system before writing down the equations).

A schematic of allosteric inhibition is shown in Fig. 1.9, alongside allosteric activation. The latter can be seen as the complementary process, where an activator is required to enhance the role of the enzyme: like the enzyme, it is not used up in the reaction, but its presence affects the overall reaction rate.
The rate of formation of product is now:

V¼

Vmaxs

Km þ ð1 þ i=KiÞs

ð1:31Þ

This is quite similar to the previous equation, but you should be able to spot the difference in its behaviour. In practice this result is only true for an allosteric

Fig. 1.9 Allosteric inhibition and activation (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)


<!-- ===== Page 31 ===== -->

18

1 Cell Structure and Biochemical Reactions

inhibitor that is uncompetitive, i.e. one that doesn’t bind to E to form EI. It is of course possible to have inhibitors that are both allosteric and competitive in which case the analysis becomes more complex. We won’t go into these, as there are more detailed treatments of these elsewhere. However, you have by now at least got an idea of how we write down reaction equations and how we analyse them. Anything else may be more complex, but every system will be analysed in the same way.

1.4 Conclusions
In this chapter we have looked at how human cells are constructed, what substances they are made of and considered how to analyse simple chemical processes using reaction equations. You should now be familiar with the basic make-up of cells and be able to understand how to write down any system of reactions, using both diagrammatic form and reaction equations, and to do some basic analysis.


<!-- ===== Page 32 ===== -->

Chapter 2
Cellular Homeostasis and Membrane Potential

2.1 Membrane Structure and Composition
The human cell can be considered to consist of a bag of ﬂuid with a wall that separates the internal, or intracellular, ﬂuid (ICF) from the external, or extracellular, ﬂuid (ECF): this wall is termed the plasma membrane. The membrane consists of a sheet of lipids two molecules thick: lipids being molecules that are not soluble in water but are that soluble in oil. The cell lipids are primarily phospholipids, as illustrated in Fig. 2.1, they have one end that is hydrophilic and one that is hydrophobic (are attracted to and repelled by water molecules respectively). The hydrophobic ends tend to point towards each other, and away from the aqueous environments inside and outside the cell, hence the two molecule thickness.
Substances can cross the membrane if they can dissolve in the lipids, which will not be true of most of the species that are in aqueous solution, such as ions. However, some electrically charged substances, which cannot readily pass through the lipid sheets, do cross the membrane. This is because the membrane is full of various types of protein molecules, some of which bridge the lipid layer. Sometimes these form pores or channels through which molecules can pass. Figure 2.2 shows a schematic of the membrane structure.
Outside the cell, the main positively charged ion is sodium (Na+) with a small amount of potassium (K+) and chloride (Cl−) ions, Table 2.1. The relative quantities are reversed in the ICF. The balance of charge is provided inside the cell by a class of molecules that include protein molecules and amino acids (likewise outside the cell, but these will be ignored here). One of the key features of the cell is the balance of molecules between the inside and outside, yet at ﬁrst glance it doesn’t appear that is the case for the cell in Table 2.1. It also does not seem obvious why the individual molecules do not diffuse in and out of the cell such that the ICF and ECF concentrations are equal. In general we are interested in how the cell maintains its internal conditions despite what is going on outside: the property called

© Springer International Publishing Switzerland 2016

19

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_2


<!-- ===== Page 33 ===== -->

20

2 Cellular Homeostasis and Membrane Potential

Fig. 2.1 The structure of a phospholipid with both hydrophobic and hydrophilic ends (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/ licenses/by/3.0/)
Fig. 2.2 Schematic of membrane structure (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)


<!-- ===== Page 34 ===== -->

2.1 Membrane Structure and Composition

21

Table 2.1 Compositions of intracellular and extracellular ﬂuids for a typical cell

Internal concentration (mM)

External concentration (mM)

K+

125

5

Na+

12

120

Cl−

5

125

P−*

108

0

H2O

55,000

55,000

*P refers to non-ionic substances, largely proteins and amino acids, inside the cell that are changed.

The overall net charge is negative

homeostasis. If we want to understand how the cell maintains this imbalance we ﬁrst need to consider the balance of cell volume.

2.2 Osmotic Balance
Consider a litre of water with 1 mol of dissolved particles: this is termed a 1 molar, or 1 M, solution, as we saw in Chap. 1. Now consider two adjacent identical volumes with different molarities (say 100 and 200 mM) and a barrier between them. If the barrier allows both water and the solute to pass, equilibrium will be reached with equal levels of the solute (150 mM) and the barrier will not move, as might be expected. However, if the barrier allows only water to cross, enough water will have to cross the barrier for the concentrations to balance and the barrier will thus move. Equilibrium will then be reached with the same concentrations (150 mM) but different volumes, 2/3 and 4/3 L, as illustrated in Fig. 2.3. The volumes are calculated by remembering that the concentrations must balance and that the number of moles of the solute cannot change. This process can be thought analogous to pressurised chambers with initial pressures (equivalent to the concentrations) and volumes: the barrier is like a piston, moving until pressure equilibrium is reached.
Now consider a slightly different example with a cell with an intracellular concentration of a substance P and an extracellular concentration of a substance Q: neither P nor Q is able to cross the membrane. There are three possibilities:
1. The concentration of Q is equal to that of P (isotonic): cell volume remains constant.
2. The concentration of Q is greater than that of P (hypertonic solution): cell volume decreases and the cell ultimately collapses if the difference in concentration is sufﬁciently large.
3. The concentration of Q is less than that of P (hypotonic solution): cell volume increases eventually rupturing the membrane if the concentration difference is sufﬁciently large.


<!-- ===== Page 35 ===== -->

22

2 Cellular Homeostasis and Membrane Potential

Water & solute can cross barrier

1l

1l

100mM 200mM

1l

1l

150mM 150mM

Water only can cross barrier
2/3 l 4/3 l
150mM 150mM

Fig. 2.3 Example of balance of concentration with solute able to cross (left) and with solute unable to cross (right)

Fig. 2.4 Cell behaviour in solutions of different concentration. Neither P nor Q are able to cross the cell membrane, any adjustments in concentration can only occur by movement of water, i.e. osmosis

A hypotonic solution is deﬁned as one that makes the cell increase in size and a hypertonic solution is one that makes the cell decrease in size. An illustration of the three types of behaviour is shown in Fig. 2.4.


<!-- ===== Page 36 ===== -->

2.2 Osmotic Balance

23

Exercise A
For the following case determine the ﬁnal, equilibrium, cell volume given the starting conditions and an initial cell volume V0.

So far we have only considered what happens if water can cross the membrane: if Q (or P) is able to cross the membrane, then the cell behaves differently. The concentration of Q must be the same inside and outside the cell: however, the total concentration inside and outside the cell must also be the same otherwise the membrane will move to adjust the concentrations.
Exercise B If Q is now able to cross the membrane determine the ﬁnal, equilibrium, cell volume given the starting conditions and an initial cell volume V0. Assume that the concentration of the species, Q, that is outside the cell is ﬁxed.
Note that in Exercise B it doesn’t matter that the total internal and external concentrations are equal unlike in exercise A where this led to equilibrium. It is also


<!-- ===== Page 37 ===== -->

24

2 Cellular Homeostasis and Membrane Potential

worth questioning the assumption that the concentration of Q is ﬁxed and not altered by Q moving into the cell. This stems from an assumption that the extracellular space is a lot larger than the cell itself and/or can easily be replenished from elsewhere, i.e. that there is an inﬁnite reserve of Q in this case.
The requirement for the total concentration to be equal inside and outside the cell is actually a requirement that the concentration of water balances. It might seem strange to talk about water concentration since there is so much of it compared to the other species, but osmosis is essentially the process of balancing water concentration.
The total concentration is often referred to as the osmolarity: the higher the osmolarity the lower the concentration of water and vice versa. A solution containing 0.1 M glucose and 0.1 M urea would have a total concentration of non-water species of 0.2 M and thus an osmolarity of 0.2 Osm. Care needs to be taken with solutions of substances that dissociate, for example, a 0.1 M solution of NaCl is a 0.2 Osm solution since you get free Na+ and Cl−. In practice the osmolarity could be lower than this if the ions in solution interacted, but this is not common in biological systems.

Exercise C
For the following cases determine the ﬁnal, equilibrium, cell volume given the starting conditions and an initial cell volume V0.

We have considered how the cell might maintain its volume despite imbalances in the concentrations of species inside and outside the cell. In fact we have met our ﬁrst principle, the principle of concentration balance.


<!-- ===== Page 38 ===== -->

2.3 Conservation of Charge

25

2.3 Conservation of Charge

Now consider the slightly more complex example in Fig. 2.5, which is a very basic model of a cell. Inside the cell are found organic molecules, P, which cannot pass through the barrier. The internal Na+ is also trapped, whereas Cl− can pass freely through the barrier. The concentrations of P and Na+ inside the cell are 100 and 50 mM respectively.
To analyse this model, there are two quantities that must be in balance: charge and concentration. The fact that the positive and negative charges must balance within any compartment is called the principle of electrical neutrality, which states that the bulk concentration of positively charged ions must equal the bulk concentration of negatively charged ions. Essentially this is due to the fact that under biological conditions, so few positively and negatively charged ions have to move to generate any membrane potential (which we will meet later) that we can assume that they balance at all times.
From charge balance:

a = 50

ð2:1Þ

b=c

ð2:2Þ

From total concentration balance:

50 þ a þ 100 ¼ b þ c

ð2:3Þ

Hence:

b ¼ c ¼ 100

ð2:4Þ

Note that, unlike in the previous section, the concentrations of Cl− are not equal inside and outside the cell: this is due to the inﬂuence of the charge balance. In fact at this point we can more carefully deﬁne the principle of concentration balance to only refer to the concentrations of uncharged species. For a simple cell model the only uncharged species that can freely cross the membrane to any signiﬁcant degree is water, thus the principle of concentration balance might be called the principle of osmotic balance.

Fig. 2.5 Cell model example

50 mM Na+
a Cl100 mM P

Na+ b Cl- c


<!-- ===== Page 39 ===== -->

26
2.4 Equilibrium Potential

2 Cellular Homeostasis and Membrane Potential

So far we have only considered concentration equilibrium: however, there is another important factor that drives ions across a cell membrane. In addition to the concentration gradient that drives ions from a region of high concentration to a region of low concentration, there is an electrical potential difference across the membrane.
For the membrane shown in Fig. 2.6, the difference in voltage between the inside and the outside of the cell is given by the Nernst equation:

 RT ½Xout

EX ¼ Vin À Vout ¼ ln

;

ZF ½Xin

ð2:5Þ

where R is the gas constant, T is absolute temperature (in Kelvin), Z is the valence of the ion and F is Faraday’s constant (96,500 C/mol_univalent_ion). The quantity in the equation above is known as the equilibrium potential and only applies for a single ion that can cross the barrier. At standard room temperature, the equation can be re-written as:

58 mV

 ½ X out

EX ¼

log10

;

Z

½ X in

ð2:6Þ

where we have changed from a natural logarithm to a base-10 logarithm. There can only be a single potential across the membrane, the membrane
potential, thus if there are two ions that can cross the membrane (in the real cell these are K+ and Cl−), then the equilibrium potential must be the same for both. Hence:

½K þ out

½ClÀ out 

Em ¼ 58 mV log10 þ ¼ À58 mV log10 À ;

½K in

½Cl in

ð2:7Þ

which on re-arranging becomes:

½K þ out ¼ ½ClÀ À in : ½K þ in ½Cl out

ð2:8Þ

This is known as the Donnan or Gibbs-Donnan equilibrium equation.

[X]in Vin

[X]out Em= Vin - Vout
Vout

Fig. 2.6 Membrane and membrane potential


<!-- ===== Page 40 ===== -->

2.4 Equilibrium Potential

27

Exercise D
Suppose that two compartments, each of one litre in volume, are connected by a membrane that is permeable to both K+ and Cl−, but not permeable to water or the protein X. Suppose further that the compartment on the left initially contains 300 mM K+ and 300 mM Cl−, while the compartment on the right initially contains 200 mM protein, with valence −2, and 400 mM K+.
(a) Is the starting conﬁguration electrically and osmotically balanced? (b) Find the concentrations at equilibrium. (c) Why is [K+] in the right compartment at equilibrium greater than its
starting value, even though [K+] in the right compartment was greater than [K+] in the left compartment initially? Why does K+ not diffuse from right to left to equalize the concentrations? (d) What is the equilibrium potential difference?

Exercise D is an interesting example of the counter intuitive differences in ion concentration that can arise due to the balance of electrical conﬁguration. However, it is not like our cell model because we had only a ﬁxed total amount of each ion available and the whole system was thus closed.

2.5 A Simple Cell Model
We started out by trying to understand cell homeostasis and how an imbalance in concentrations of ions inside and outside of the cell could be maintained. We now have three principles to apply when we analyse cell concentrations:
1. Concentration (osmotic) balance. 2. Electrical neutrality. 3. Gibbs-Donnan equilibrium.
We are now ready to try and build a simple model of a cell at equilibrium, Fig. 2.7. Inside the cell is found Na+, K+ and Cl− as well as some negatively charged particles, termed P, that represent an array of different molecules, including

a Na+

b

K+

c

Cl-

108 mM P -11/9

Fig. 2.7 A simple cell model

Na+ 120 mM K+ 5 mM Cl- d


<!-- ===== Page 41 ===== -->

28

2 Cellular Homeostasis and Membrane Potential

proteins. Outside the cell is found Na+, K+ and Cl− where K+ and Cl− are free to cross the membrane.

Exercise E
Figure 2.7 is incomplete since some of the concentrations have not been given.
(a) Write down and solve the appropriate equations to calculate the unknown concentrations in the ﬁgure. Note that the charge of P is −11/9 (about −1.22),1 which means that the charge equilibrium equation must be written down carefully.
(b) What is the value of the membrane potential in this example? (c) If the cell membrane was permeable to sodium, calculate the equilibrium
potential for sodium. What would happen to the cell?

This exercise takes us close to a realistic model of the cell: you should ﬁnd that the values of concentration that you get are the same as Table 2.1. Note that it will remain in this state indeﬁnitely without the expending of any metabolic energy: a very efﬁcient structure. However, you will have found that if the cell is permeable to Na+, its equilibrium potential is very different from the membrane potential you calculated when the membrane is impermeable to Na+. Thus if the membrane were permeable to sodium then it would be impossible to achieve equilibrium due to the proteins etc also present in the cell: the cell would grow until rupture.
2.6 Ion Pumps
Unfortunately, the real cell actually does expend metabolic energy in order to remain at equilibrium. The reason for this is that the cell wall is actually permeable to Na+, which implies that our model cell will not remain in an equilibrium state. The answer to this problem is that there is something called a sodium pump, which we will now examine brieﬂy.
An ion pump is a mechanism that absorbs energy to move ions against a concentration or electrical gradient, rather like a heat pump. The ion pump gets its energy from ATP as we met in Chap. 1. For Na+, as fast as it leaks in due to the concentration and electrical gradients, it is pumped out. Na+ thus effectively acts as if it cannot cross the membrane, but the cell is now a steady state, requiring energy, rather than an equilibrium state, which requires no energy.
1Some other texts round down to a charge of −1.2, which appears to be very close to that here, but will result in quite different concentrations for some of the ions if you try to use it.


<!-- ===== Page 42 ===== -->

2.6 Ion Pumps

29 Na+

K+
Fig. 2.8 The sodium/potassium pump
The common symbol for the pump is shown in Fig. 2.8, which also shows that the pump needs K+ ions outside the cell to pump inside in return for Na+ ions inside. The protein on the cell outer surface needs K+ to bind to it before the protein can return to a state in which it can bind another ATP and sodium ions at the inner surface. Since the K+ ions bound on the outside are then released on the inside, the pump essentially swaps Na+ and K+ ions across the membrane and is thus more correctly known as the Na+/K+ pump and the membrane-associated enzyme as a Na+/K+ ATPase. We will revisit the ion pump in Chap. 4.

2.7 Membrane Potential

Now that we have reconsidered the cell as a steady state device (rather than an

equilibrium device), we need to reconsider the membrane potential. Previously in Exercise E we had Em = EK = ECl = −81 mV. However, now we also have a contribution from Na+ with ENa = +58 mV, the membrane potential will have to
settle somewhere between these extremes. This actually depends upon both the

ionic concentrations and the membrane permeability to the different ions. Clearly if

the permeability to a particular ion is zero, it contributes nothing to the potential,

whereas with a high permeability it contributes signiﬁcantly more. The permeability

of the membrane to different ions is absolutely vital in our understanding of the

operation of the cell.

The permeability of a membrane to a particular ion is simply a measure of how

easily those ions can cross the membrane. In electrical terms, it is equivalent to the

inverse of resistance (i.e. conductance). We will consider why the permeabilities are

different for different ions in Chap. 3, but for now, we will note that the perme-

ability is related to the number of channels that allow the ions to pass through and

the ease of passage through the channels.

The relationship between membrane potential and the concentrations and per-

meabilities of the different ions in the cell is known as the Goldman equation:

pK½K þ o þ pNa½Na þ o þ pCl½ClÀi

Em ¼ 58 mV log10

þ

þ

À;

pK½K i þ pNa½Na i þ pCl½Cl o

ð2:9Þ

where p denotes permeability. Note that because Cl− has a negative valence the inner and outer concentrations are the opposite way round to those for Na+ and K+.
For a membrane that is permeable to only one ion, the Goldman equation reduces
immediately to the Nernst equation.


<!-- ===== Page 43 ===== -->

30

2 Cellular Homeostasis and Membrane Potential

In practice, the contribution of Cl− is negligible and hence the equation is usually encountered in the form:

½K þ o þ b½Na þ o

Em ¼ 58 mV log10 þ

þ;

½K i þ b½Na i

ð2:10Þ

where in the resting state b ¼ pNa=pK is approximately 0.02. For the typical resting state with the concentrations given previously, the membrane potential is approximately −71 mV. The membrane potential is closer to the value for K+, since the permeability to K+ is much greater than that for Na+. However, changes in the
relative permeability can produce large changes in the membrane potential between
these two values. Since the membrane potential is equal to neither the values for Na+ nor for K+,
there is a leakage of both K+ out of and Na+ into the cell: hence the role of the Na+/ K+ pump to maintain the membrane potential at a steady state value. A more
complete model for cell is shown in Fig. 2.9 that also includes the forces acting on
the ions. Note that the net charge on the inside of the cell is negative therefore the electrostatic forces acting on both Na+ and K+ in inward, whereas on Cl− it is outward. It is easy to see why at the very least a pump for Na+ is required.
Although we have ignored Cl− in the calculation of the membrane potential, it is affected by it: the equilibirum membrane potential for Cl− is −80 mV, so either the concentration will change (as in some cells) or a Cl− pump is used to maintain a steady state level of Cl−. Less is known about this pump than the Na+/K+ pump.
Since a difference in membrane potential from the equilibrium value for an
individual ion causes a movement of ions across the membrane we can introduce a
new concept, that of membrane conductance, as deﬁned by:

iK ¼ gKðEm À EKÞ;

ð2:11Þ

iNa ¼ gNaðEm À ENaÞ;

ð2:12Þ

iCl ¼ gClðEm À EClÞ:

ð2:13Þ

Fig. 2.9 Steady state cell model, showing the electrical (E) and chemical (C) forces acting on the ions

12 mM Na+ 125 mM K+
5 mM Cl-

E
Na+ 120 mM
C
K+ 5 mM
Cl- 125 mM

108 mM A-11/9 K+

Na+ Em = -71 mV


<!-- ===== Page 44 ===== -->

2.7 Membrane Potential

31

Em iK

gk=1/Rk Ek

in out

Fig. 2.10 Modelling the cell membrane as a resistance/conductance for each ion

Since Em ¼ À71 mV; EK ¼ À80 mV and ENa ¼ 58 mV from above, the potassium current is positive and the sodium current is negative. By convention, an outward current is positive and an inward current is negative. In the steady state the net current is zero, which is the basis of the Goldman equation. The conductance is related to both the permeability and the number of available ions in the solution. Note that conductance is the inverse of resistance and so in electrical terms, the membrane can be considered as a resistor as in Fig. 2.10.
The meaning of permeability can be explored in more detail by remembering that the membrane is full of protein channels that permit different ions to pass through. These channels can be considered to be controlled by a gate that is either open or closed (this mechanism is known as channel gating). Although the channels are slightly more complicated than this, it is a valid ﬁrst approximation: we will examine this in more detail in Chap. 3. Rather like an electrical switch, each channel is thus either ‘on’ or ‘off’ as far as current is concerned. Since there are a very large number of channels, the permeability of the membrane can be controlled to a high degree of accuracy by the opening of different numbers of channels. This ability to change the membrane permeabilities is a major factor in the behaviour of cells and this will be examined in Chap. 3 when we consider the action potential.

Exercise F
A simple model for a cardiac myocyte (heart muscle cell) can be built using the concentrations of the ions to which the membrane is permeable given in the table.

Ion

Internal concentration (mM)

External concentration (mM)

Na+

10

145

K+

140

4

Cl−

30

114

Ca2+ 10−4 1.2

(a) Calculate the equilibrium potentials for all the ions in the cardiac myocyte and hence determine if the cell is in equilibrium.


<!-- ===== Page 45 ===== -->

32

2 Cellular Homeostasis and Membrane Potential

(b) Using the principles of electrical neutrality and osmotic balance determine the internal concentration and overall charge of other charged species (e.g. proteins) within the cell that are unable to cross the cell membrane, assuming zero external concentration of any other species.
(c) Show that this cardiac myocyte cell is not in a steady state.

This ﬁnal exercise explores a cell with a speciﬁc function that we will meet in Chap. 7. Whilst a lot of the values for ionic concentrations, charges and potentials are not wildly different from the model cell we have considered in this chapter, this cell is neither in equilibrium nor even in steady state. We might have been wrong to ignore any other charged species outside the cell. Otherwise, like the simple cell model, we might worry that this cell would expand until rupture. Note that ions pumps wouldn’t help here as the concentrations we have do not satisfy all the principles and thus the cell cannot be in steady state; the ion pumps only helped to maintain the steady state in the simple cell model. It turns out that cardiac myocytes never reach a steady state and the concentrations ﬂuctuate over a cycle, these values (probably) just representing the ‘resting’ state. We will return to this in Chap. 7.

2.8 Conclusions
In this chapter we have considered how the cell can maintain homeostasis despite differences in concentration of ions and other charged species both inside and outside of the cell membrane. You should now understand the principles of concentration balance, electrical neutrality and Gibbs-Donnan equilibrium and be able to apply them to a cell model. You should also be able to calculate equilibrium potentials for individual ions as well as the membrane potential and understand why these are not always the same value. Finally you should now appreciate why cells use energy to maintain homeostasis.


<!-- ===== Page 46 ===== -->

Chapter 3
The Action Potential

3.1 Na+/K+ Action Potential

As we saw in Chap. 2, it is the relative permeability of the membrane to Na+ and K+ that determines the membrane potential.

½K þ o þ b½Na þ o

Em ¼ 58 mV log10 þ

þ:

½K i þ b½Na i

ð3:1Þ

In the resting state, the ratio is 0.02, as given in Chap. 2, but if the membrane permeability to Na+ were suddenly increased by a signiﬁcant factor, this ratio would increase and the membrane potential swing from close to EK (−80 mV) to close to ENa (+58 mV). This is essentially all that is required to generate the action potential, which is a transient change in the membrane potential of the cell. The
action potential arises because the gates which determine the permeability of the
membrane are controlled by the membrane potential.

Exercise A
Calculate the membrane potential if b were to increase by three orders of magnitude to 20, assuming that the ionic concentrations are still at the steady state values in Table 2.1. What would be implications for the ionic concentrations of this change?

Since Em is a logarithmic function of the relative permeability it takes orders of magnitude changes in b to make a substantial difference. You will have noticed in
Exercise A that an increase in relative permeability either implies that the permeability to K+ has reduced or to Na+ has increased, in practice it is the latter.

© Springer International Publishing Switzerland 2016

33

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_3


<!-- ===== Page 47 ===== -->

34

3 The Action Potential

A change in permeability will lead to a ﬂow of ions driven by the different
membrane potential, the cell will no longer be in steady state.
A typical action potential is shown in Fig. 3.1, this would correspond to a nerve
cell: we will see examples of variants on this later. The process of the action
potential follows these steps, summarised in Fig. 3.2 and Table 3.1:
(A) Resting state: The number of Na+ channels that are open are small and b = pNa /pK * 0.02.
(B) Depolarization: If the membrane potential becomes more positive then more Na+ channels open, thus b will increase and Em will become even more positive. This positive feedback loop means that there is a large and rapid swing in Em, meaning that the action potential continues irrespective of any further external inﬂuence. Thus the action potential is known as an ‘all or nothing’ event.
(C) Repolarization: The Na+ channel actually has two gates: m that is normally closed and h that is normally open. Upon depolarization m opens rapidly, but h closes much more slowly and it is this timing difference that leaves time for
depolarization before repolarization kicks in. Additionally, there are voltage sensitive K+ channels with n gates that are normally closed that also respond slowly to the depolarization. Thus pK also increases on depolarization and like the h gate this drives Em back toward the resting value. (D) Undershoot: Due to the n gates pK is greater than usual so that b ends up being smaller than the resting value, which causes Em to undershoot until the n gates eventually return to normal.
(E) Refractory period: Whilst the membrane potential may have returned to the resting state the h gates will initially still be shut blocking the Na+ channels even if the m gates were to reopen. Thus there is a period in which a new
action potential cannot be generated. In practice the undershoot and refractory

Fig. 3.1 The membrane potential during a typical (nerve cell) action potential


<!-- ===== Page 48 ===== -->

3.1 Na+/K+ Action Potential

35

Fig. 3.2 Schematic of voltage-sensitive channels during action potential

Table 3.1 Overview of gate behaviour during an AP

Phase

Na+ gates

m

h

A: Resting state Closed

Open

B: Depolarising Opens quickly Closes slowly

C: Repolarising Open

D: Undershoot Closing quickly Closed

E: Refractory Closed

Opening slowly

K+ gate n Closed Opens slowly
Open Closing slowly

b
*0.02 0.02 → 20 20 → *0.02 <0.02 <0.02 → *0.02

periods overlap and the extent to which it is raised K+ permeability or inability for an increased Na+ permeability that prevents another AP from ﬁring depends upon the precise timings of the gates.
In practice the action potential only occurs once a certain threshold of membrane potential is reached, usually around 10–20 mV above its resting value. For smaller depolarization the efﬂux of K+ induced by the change in Em exceeds the efﬂux of Na+ , leading to a negative feedback process that suppresses further depolarization. The actual value of this threshold depends upon a variety of factors, particularly the packing density of the Na+ channels and the relationship between the membrane potential and the opening pattern. Some neurons are highly sensitive, whilst others require a very large depolarization to stimulate a action potential.


<!-- ===== Page 49 ===== -->

36
3.2 Ca2+ Contribution

3 The Action Potential

Action potentials do not only occur in neurons: they can be found in muscle cells, as will be considered later. In most neurons, however, voltage-dependent Ca2+
channels are also found, which can contribute signiﬁcantly to the action potential. This is because they often inactivate more slowly than the corresponding Na+
channels, causing a much slower repolarization with a plateau phase caused by the Ca2+ channels and the increase in intracellular Ca2+. This increase can be important
in its own right: in Chap. 4 we will see that this is the trigger for the release of
neurotransmitters, which are important in cell-cell communication. Intracellular Ca2+ can also activate other kinds of ion channels (often K+
channels that are activated by Ca2+), which can lead to a hyperpolarizing undershoot after repolarization due to the increase in pK. Since the increase in Ca2+ concentration lasts much longer than the normal timing of the action potential, the
resulting hyperpolarization is some hundreds of times longer than it. This effect is
particularly important for heart muscle cells, as we will see in Chap. 7. This is dependent on having enough Ca2+ inﬂux during the action potential and enough Ca2+ activated K+ channels.
In some case the levels of Ca2+ may build up gradually over many action potentials before it is sufﬁcient to activate the K+ channels and to cause hyperpo-
larization (normally called the after-hyperpolarization to distinguish it from the
undershoot). This can be a way of obtaining rhythmic bursts of activity punctuated
by periods of silent behaviour, particularly in neurons that control rhythmic events,
which we will meet in Chap. 7.

3.3 Hodgkin-Huxley Model
The generation and propagation of signals have been studied for at least 100 years: however, the most important piece of work during this time was performed by Hodgkin and Huxley between 1949 and 1952. Hodgkin and Huxley studied the squid giant axon and developed the ﬁrst quantitative model of the propagation of the electrical signal. This model was such an important step in the understanding of electrical activity that it has been called “the most important model in all of the physiological literature”, Keener and Sneyd. Their approach was to model the cell as a simple electrical circuit, Fig. 3.3. The cell is assumed to have a capacitance Cm that models the insulating effects of a cell membrane that is inherently impermeable to ions. The model includes current inputs through potassium, sodium and other channels (these last being lumped together and termed leakage). There is also an applied current, which we will examine in more detail later.


<!-- ===== Page 50 ===== -->

3.3 Hodgkin-Huxley Model

37

Fig. 3.3 Schematic of Hodgkin-Huxley model

Exercise B
Starting with the simple cell model in Fig. 3.3 use current balance to derive a differential equation for the electrical properties of the cell.

The Hodgkin-Huxley model starts from applying current balance to the model in Fig. 3.3, as you did in Exercise B:

Cm dv ¼ ÀgKn4ðv À vKÞ À gNam3hðv À vNaÞ À gLðv À vLÞ þ Iapp; dt

ð3:2Þ

The potential, v, here is deﬁned as the deviation from the steady state value, measured in units of mV. Notice that in Eq. 3.2 gK ¼ gKn4 and gNa ¼ gNam3, the conductance’s include the variables m, n and h. These refer to the m, n and h gates
respectively (actually the gates are named after the variables named by
Hodgkin-Huxley in their model): when the values are equal to 0, the gates are closed (the ﬁrst equation shows that both m and h gates are needed for Na+ to ﬂow, but only the n gate is required for K+). The powers of m and n in the equation were
chosen based on experimental data and are often interpreted as the number of
binding sites on the two gates.
The gate parameters have their own governing equations:

dm ¼ amð1 À mÞ À bmm; dt dn ¼ anð1 À nÞ À bnn; dt

ð3:3Þ ð3:4Þ


<!-- ===== Page 51 ===== -->

38

3 The Action Potential

dh ¼ ahð1 À hÞ À bhh; dt

ð3:5Þ

Equations 3.3–3.5 are simply ﬁrst order kinetic models with forward and backward rate constants like those we met in Chap. 1. These have a sigmoidal response to a change in potential that matches that seen in experimental data, the powers on the m and n gates result in a steeper slope in their sigmoidal response. The parameters in Eqs. 3.3–3.5 are themselves non-linear functions of the voltage:

25 À v am ¼ 0:1 À25ÀvÁ ;
exp 10 À 1 Àv
bm ¼ 4 exp ; 18
10 À v an ¼ 0:1 À10ÀvÁ ;
exp 10 À 1 Àv
bn ¼ 0:125 exp ; 18
Àv ah ¼ 0:07 exp ;
20
bn ¼ À30Àv 1 Á : exp 10 þ 1

ð3:6Þ ð3:7Þ ð3:8Þ ð3:9Þ ð3:10Þ ð3:11Þ

The remaining parameters all have ﬁxed values as shown in Table 3.2.

Exercise C
A gate in a cell membrane can have one of two states: closed and open. A simple reaction diagram can thus be written to model changes between the two states:
a
CO
b
where C denotes the probability that the gate is closed and O the probability that it is open.
(a) Write down the two reaction equations governing the behaviour of this gate.
(b) What is the sum of the two probabilities? Hence write down a single equation in terms of the probability that the gate is open. How does this relate to the gate equations in the Hodgkin-Huxley model?


<!-- ===== Page 52 ===== -->

3.3 Hodgkin-Huxley Model

Table 3.2 Fixed parameter gK

values for the

Hodgkin-Huxley model

gNa

gL

vK

vNa

vL

Cm

39
36 mS/cm2 120 mS/cm2 0.3 mS/cm2 −12 mV 115 mV 10.6 mV 1 μF/cm2

(c) For the equation derived in part (b), write down the steady-state probability of the gate being open and the time constant governing its behaviour.

We will perform some simple analysis of the Hodgkin-Huxley model here to illustrate how a simple model can be used to simulate and to understand the behaviour of a physiological system. The ﬁrst thing we examine is the steady state behaviour of the variables m, n and h and the time constants. These values are plotted for a range of potential in Fig. 3.4.
Exercise D
(a) Write down expressions for the steady state probability and time constant for each of the gates in the Hodgkin-Huxley model.
(b) Using the values in Fig. 3.4, explain how the response of the different gates gives rise to the action potential.

Fig. 3.4 a Steady state values and b time constants for m, n and h as a function of v, the difference in membrane potential from its resting value


<!-- ===== Page 53 ===== -->

40

3 The Action Potential

Fig. 3.5. Time series of action potential with applied stimulus
We now apply a stimulus to the system in the form of the applied current: this is equivalent to a neighbouring cell providing a change in potential. If a small stimulus is applied, nothing happens, but if it reaches a threshold value, the action potential suddenly occurs. In Fig. 3.5, a stimulus is applied at 2 s and left on: the system ‘ﬁres’ and there is then a refractory period before it ﬁres again. Note that the m gate opens very rapidly, with the n and h gates responding more slowly, as in the model schematic shown earlier. The presence of the applied current in the model does not reﬂect a physiological current source, but that the original experiments were done by applying external electrical stimulation to excised nerve cells.
Exercise E
Implement the Hodgkin-Huxely model in a numerical mathematics package using a differential equation solver and reproduce Fig. 3.5 using an applied current of 5 μA. Determine the smallest current needed to stimulate the model.
It may seem slightly confusing that in Chap. 2 we considered Na+/K+ and Cl− ions, whereas here we have considered Na+/K+ and Ca2+ in this chapter. Na+ and K+ are the dominant ions in the cell’s behaviour, whereas the other ions play roles in different aspects of the cell’s behaviour, so have to be considered as and when they are relevant. More detailed models of the cell’s behaviour include all the different ions.


<!-- ===== Page 54 ===== -->

3.3 Hodgkin-Huxley Model

41

Exercise F
Returning to the cardiac myocyte model from exercise 2F, the following ﬁgure shows a schematic of the action potential for this cell.

(a) During periods between muscle contraction (phase 4) the membrane is found to a have a high relative permeability to potassium compared to all the other ions. Use this to explain why the membrane potential during this phase is in the range −85 to −95 mV.
(b) The plateau phase (2) is believed to be largely due to the inﬂux of calcium into the cell (through calcium-gated calcium channels). What minimum internal concentration of calcium ions could sustain this plateau? Assume that calcium permeability is far larger than that of all other ions during the plateau.
3.4 Conclusions
In this chapter we have met the action potential, the fundamental electrical signalling mechanism used by the body. You should now be able to understand the cycle of ion movements associated with the generation of an action potential and the role of different ion gates. You should also be able to analyse the system of action potential generation in terms of a simple electrical circuit model.


<!-- ===== Page 55 ===== -->

Chapter 4
Cellular Transport and Communication

4.1 Transport
One of the important processes that occurs everywhere in the body is transport: getting substances to move from one place to another. The different types of mass transport can be thought of in terms that are analogous to heat transfer, where we have conduction and both forced and natural convection. For example, ‘forced’ convective transport is achieved by pumping a ﬂuid from one place to another: this is essentially how oxygen is transported around the body, by blood being pumped through blood vessels and we will examine this in later chapters. We will consider a number of different processes here very brieﬂy that apply at the cellular level. Although there are only a handful of mechanisms that can be used and the law of conservation of mass always holds, there are many different conditions under which transport occurs.

4.1.1 Passive Transport

We have already considered how concentration differences drive species such as ions in and out of the cell. For a given entity present in solution within a region we can write down, via conservation of mass:

@c ¼ Àr Á J þ f ; @t

ð4:1Þ

which essentially says that the rate of change of the concentration c with time equals the rate of production of the substance within the region, f, and the rate at which it leaves across the surface of the region, which is determined by the

© Springer International Publishing Switzerland 2016

43

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_4


<!-- ===== Page 56 ===== -->

44

4 Cellular Transport and Communication

ﬂux J. Intuitively we expect the ﬂux should be related to the concentration gradient, which is the basis of Fick’s law:

J ¼ ÀDrc;

ð4:2Þ

If we substitute that into the conservation law then we arrive at the diffusion equation:

@c ¼ Dr2c þ f ; @t

ð4:3Þ

where in this case we have assumed that D, the diffusion co-efﬁcient, is constant across space. Since no energy is involved, diffusion is a passive means of transport. The value of D is related to the size and geometry of the chemical species as well as things like temperature and viscosity. If the size of the solute is much greater than that of the solvent then an estimate of D can be found from the Stokes-Einstein equation:

D ¼ kT ; 6pla

ð4:4Þ

where k is the Boltzmann constant, μ is viscosity and a is the radius of the molecule assuming an approximately spherical shape. We can re-write this in terms of the molecular weight:

kT  q 31

D¼

2;

3l 6p M

ð4:5Þ

where, since ρ is approximately constant for large protein molecules we arrive at the result that D / MÀ1=3, whereas for smaller molecules, for example respiratory molecules, D / MÀ1=2 turns out to be more accurate.
In the simplest case passive transport of a species through a cellular membrane between an external concentration co and internal concentration ci can be described by the formula for ﬂux:

J ¼ DK ðci À coÞ; L

ð4:6Þ

where D is the diffusivity of the species in the membrane, L is the membrane thickness and K is the partition coefﬁcient. Note that the ﬂux is simply linearly dependent upon the concentration difference. The partition coefﬁcient describes the
relative solubility of the species in the membrane as compared to the external (and internal) environments. For a cell this would reﬂect the typically poor solubility of
many solutes in the lipid membrane region compared to the aqueous environments
either side of the membrane. It is this relatively poor solubility that means few species pass directly through the cell membrane in any signiﬁcant quantity.


<!-- ===== Page 57 ===== -->

4.1 Transport

45

The combination DK/L is often termed the permeability, since these terms all relate to properties of the membrane for the species that determine how permeable the membrane appears.

Exercise A The ﬁgure shows a simple 1-dimensional model of a cell membrane through which a species might permeate, with thickness L and diffusivity D. Using the
diffusion equation derive an expression for the concentration as a function of x and thus derive an expression for the ﬂux.

Redraw the ﬁgure if the species is twice as soluble in the membrane compared to the external (and internal) solute.
4.1.2 Carrier-Mediated Transport
Some substances are insoluble in the cell membrane, yet pass through by a process called carrier-mediated transport. Essentially a substance combines with a carrier protein at the outer membrane boundary and by means of a conformational change is released on the inside of the cell. This is still essentially a passive transport process since no energy is involved. One of the most important examples of this is the transport of glucose into the cell to provide a source of energy.
Although the precise mechanics of this process are not completely understood, a simple model for this transport is that the glucose substrate binds with an enzyme carrier protein to form a complex, which can change (the conformational change) from an ‘internal’ carrier to an ‘external’ carrier and vice versa. The external carrier can reduce to the glucose substrate outside the cell with the enzyme carrier protein in its ‘external’ state, which then reduces to an ‘internal’ state. This is shown in the


<!-- ===== Page 58 ===== -->

46

4 Cellular Transport and Communication

Fig. 4.1. A model reaction scheme for carrier-mediated transport of a substance S across a cell membrane by means of a carrier C
reaction scheme in Fig. 4.1. Notice the similarities with the enzyme reaction models in Chap. 1.

Exercise B Using the reaction scheme in Fig. 4.1, write down the differential equations for each of the four states of the carrier.

Analysis of this is pretty complicated, but quite possible using the mathematics we used in Chap. 1. It turns out that in the steady state we can calculate the rate of supply and demand, J:

J ¼ kÀpi À k þ sici ¼ k þ sece À kÀpe;

J ¼ 1 KdKk þ Co

2 se À si ;

2

ðsi þ K þ KdÞðse þ K þ KdÞ À Kd

ð4:7Þ ð4:8Þ

where K ¼ kÀ=k þ ; Kd ¼ k=k þ and Co ¼ pi þ pe þ ci þ ce, the total amount of the carrier present in any form. The most important features of this are that at low levels ﬂux transport is proportional to concentration difference, so it looks like a diffusion
process, and that there is saturation at high levels of external glucose. Although the
system looks more complicated, the essentials of its behaviour are not that far away
from the simple Michaelis-Menten kinetics we met in Chap. 1.

4.1.3 Active Transport
The processes considered thus far are all passive processes, where ions move down pressure or concentration gradients. There are many processes, however, that require energy to take place, and are thus termed active transport. A case of this is where the concentration of the species inside the cell is actively reduced thus maintaining the concentration gradient required for the passive transport process.


<!-- ===== Page 59 ===== -->

4.1 Transport

47

For example, glucose is rapidly bound within the cell keeping its concentration low;
this phosphorylation of glucose requires hydrolysis of ATP. Another case is the ion pumps we saw in Chap. 2, where a Na+/K+ pump was
used to keep the levels of Na+ high outside the cell and K+ high inside the cell. This
requires energy to overcome the gradients and this energy was supplied in the form of ATP. Since the Na+/K+ pump is essentially a reaction, we can write down a
reaction equation for it:

ATP

þ

3Na

þ i

þ

2K

þ e

!

ADP þ Pi þ 3Naeþ

þ

2K

þ i

:

ð4:9Þ

However, this is a rather simpliﬁed version of the actual processes. A more precise schematic is shown in Fig. 4.2. In its dephosphorylated state, Na+ binding
sites are exposed to the intracellular space; when these ions are bound, the carrier
protein is phosphorylated by the release of energy involved in ATP converting to ADP. This exposes the Na+ binding sites to the extracellular space, reducing the binding afﬁnity of these sites and releasing the bound Na+. A similar process happens, but from extracellular to intracellular, for K+.
This can be converted into a mathematical model by writing down three reaction equations (which we won’t do here). Note that this is still a simpliﬁed version, where the rate of exchange is one Na+ for one K+ ion, rather than the actual three for two. The corresponding differential equations can be written down (again we won’t do this here as it is lengthy), where the intracellular Na+ and extracellular K+ are supplied at a constant ﬂux J (and extracellular K+ and intracellular Na+ are
removed). In the steady state, this rate can be expressed as:

J ¼ CoK1K2 À þ

½

Na

þ i

½

K þe



þÁ

þ

;

½Ke K2 þ ½Ki KÀ2 Kn þ ½Nai K1Kk

ð4:10Þ

where the rate constants are functions of the individual rate constants in the detailed model. The important features of this are that it is very similar to an enzyme reaction, i.e. it has dynamics similar to a Michaelis-Menten reaction, being nearly linear at small concentrations of intracellular Na+ and saturating at large concentrations.

Fig. 4.2. Schematic of Na+/K+ pump


<!-- ===== Page 60 ===== -->

48
4.2 Cellular Communication

4 Cellular Transport and Communication

So far, we have considered the cell largely in isolation: we now need to think about how information is passed between cells. Like transport there are processes happening both at the cellular and systemic level. In the latter case the bloodstream is involved as a means to transport signalling chemicals, hormones, from one cell or group of cells where the hormone is produced to another region where the signal is ‘received’. This is the responsibility of the endocrine system and can be seen as a way to broadcast information throughout the body. A similar, but more local system, of communication is achieve by the paracrine system, where local ‘mediator’ chemicals are released by the signalling cell and received by neighbouring target cells.
In this chapter we will be more interested in direct signalling between cells. One way of signalling is contact-dependent, where the signalling molecule is physically bound to the cell membrane of the signalling cell. This requires cells to come into contact with the target cell and thus only really applies to mobile cells.

4.3 Synapses
An important role of cell-to-cell communication is the passing of action potentials that we met in Chap. 3. There are two ways in which information of this form can be passed: electrical and chemical. The point where the transfer takes place is termed a synapse: there are thus both electrical and chemical synapses. In both cases there are special structures at the point where the input cell, the presynaptic cell, communicates with the output cell, the postsynaptic cell.
Exercise C An increase of extracellular K+ has the same effect as an applied current in the Hodgkin-Huxley model.
(a) Explain why this is the case and derive an expression that relates the necessary change in potassium equilibrium to the size of the applied current
(b) If a current of 2.3 μA can initiate an action potential calculate the equivalent change in potassium concentration required.
(c) What relative change in external potassium concentration would give rise to such a change in potassium equilibrium potential. Would a rise in extracellular Na+ also work?


<!-- ===== Page 61 ===== -->

4.3 Synapses

49

4.3.1 Electrical Synapses

In Exercise C you have explored a mechanism by which one cell could theoretically initiate an action potential in a neighbouring cell through an increase in potassium in the space between them. A similar mechanism is used at an electrical synapse; the action potential spreads directly to the postsynaptic cell. An electrical synapse is a special region of the cell where postsynaptic cell membrane touches that of the presynaptic cell and the intracellular spaces are connected through special ion channels called gap junctions. The two cells are deliberately put into close chemical contact making it easy for changes in ionic concentration in one to affect another. This is a very rapid means to pass an action potential from one cell to another and is used by cardiac muscle cells, as we will see in Chap. 6. Apart from being used to conduct electrical signals, it is also the mechanism used to co-ordinate activity in the liver.

4.3.2 Chemical Synapses
At a chemical synapse, an action potential results in the release of a chemical substance (called a neurotransmitter). This moves through the extracellular space separating the two cells, and alters the membrane potential of the postsynaptic cell. The best understood chemical synapse is the one between a motor neuron and a muscle cell, termed a neuromuscular junction, Fig. 4.3. The process proceeds as follows:
• The action potential arrives at the presynaptic cell and causes depolarization. • Depolarization causes Ca2+ channels to open. • Ca2+ enters the presynaptic cell. • Synaptic vesicles fuse with the membrane. • Neurotransmitters are released into the synaptic cleft. • Neurotransmitters bind to special channels found on the post-synaptic cell
surface. • Channels open allowing Na+ and K+ to cross, permeability of both thus
increases. • Depolarization of post synaptic cell.
Whilst the absolute permeabilities of both Na+ and K+ increase by roughly the same amount, the relative permeability to Na+ increases more since it started at a lower absolute level. This causes the membrane potential to rise by some 50–60 mV and hence an action potential is generated, the channels closing after a short time (approximately 1 ms).
The neurotransmitter in this case is called acetylcholine (ACh). This is stored in units of about 10,000 molecules and so is released in packets, or quanta: a single action potential normally results in the release of more than 100 packets. These


<!-- ===== Page 62 ===== -->

50

4 Cellular Transport and Communication

Fig. 4.3. Schematic of neurotransmitter release, (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
packets are stored in large numbers of tiny membrane-bound structures known as synaptic vesicles. ACh is released when the vesicles fuse with the muscle cell membrane at special sites called release sites or active zones, which are only found on the membrane surface opposite the postsynaptic cell. The vesicle membranes are continuously recycled, being ﬁlled, emptied and re-ﬁlled. Once outside the cell ACh is broken down by an enzyme (choline acetylcholinesterase), allowing the receptor mediated channels to close. The choline produced by the process is then taken back up into the cell and more ACh is synthesized, before being packaged into vesicles. Many other neurotransmitters exist along with a range of different channels that respond to them, allowing for a variety of different chemical synapses with different properties.
We have considered the neuromuscular junction in some detail: chemical synapses between two neurons are essentially the same, although there are some important differences. Probably the most important is that a neuron may receive synaptic connections from thousands of different neurons, unlike a muscle cell that receives an input from only one neuron as we will see in Chap. 10.


<!-- ===== Page 63 ===== -->

4.4 Action Potential Propagation

51

4.4 Action Potential Propagation

We have seen how an action potential is generated and how it can be passed from one cell to another, but it is clearly of no use if it remains isolated in one location in the cell. Instead it must be able to propagate through a cell. In particular we need to ensure that an action potential can be transmitted by nerve cells from the brain to the rest of the body (or vice versa), for example along a neuron to the neuro-muscular junction we met earlier. We might imagine that because the action potential is an electrical signal and is associated with the ﬂow of ions it could travel along a cell in the same way that an electrical signal can travel along a wire.
We can build a simple model of this process using the electrical circuit in Fig. 4.4, which is effectively the model of an electrical cable. In this model we have an inﬁnitely small segment of a cell with action potential propagation in only one-dimension ‘along’ the cell. We have modelled the interior cell as an electrically resistive medium, with resistance per unit length Rc, and the cell wall as having both capacitance and conductance per unit area of membrane of Cm and 1/Rm respectively. Thus we are including the fact the cell wall is ‘leaky’ to ions, but we are simplifying the problem by ignoring the contributions from different ions that we had in the Hodgkin-Huxley model. We are also ignoring any resistance to current in the extra cellular space, effectively assuming that there is a larger volume for conductance there than inside the cell. Using this model we can get a general solution for the potential as a function of both time and space (length along the cell in this one-dimensional case), the cable equation:

2 @2V

@V

km 2 ¼ sm þ V ;

@x

@t

ð4:11Þ

qﬃﬃﬃﬃ where sm ¼ RmCm is the membrane time constant and km ¼ RRmc is the cable

space constant.

Fig. 4.4. The cable model of passive action potential propagation along a cell


<!-- ===== Page 64 ===== -->

52

4 Cellular Transport and Communication

Exercise D
(a) Starting with Fig. 4.4 derive the cable equation in Eq. 4.11. Note that by convention Rc is a resistance per unit length of cell, but Cm and Rm are deﬁned per unit area of membrane.
(b) By convention properties of the membrane are quoted as speciﬁc resistance and speciﬁc capacitance for a unit area of membrane, rm and cm respectively. Properties of the space inside the cell are given as speciﬁc resistance of a unit (cross sectional) area of cytoplasm, rc. For a cell of diameter d, rewrite the membrane time and cable space constants in terms of these properties.
(c) Calculate the membrane time and cable space constants for a cardiac cell with d = 20 μm, rc = 150 Ω cm, rm = 7 × 103 Ω cm2 and cm = 1.2 μF/cm2.
(d) Consider the behaviour of the system under steady state conditions. If one end of the cell is 100 mV above resting potential at what maximum distance could an action potential be induced, if a threshold (above resting potential) of 20 mV is required to initiate an action potential?

The analysis from Exercise D implies that a change in potential at one point in the cell could initiate another action potential at a distance of the order of 1 mm along the cell. This would be acceptable for the propagation of the action potential in a cardiac muscle cell, which is of the order of 0.1 mm in length, but clearly isn’t suitable for nerve cells who have cell bodies metres in length. The analysis in Exercise D was relatively simplistic, and we could be more thorough and specify appropriate boundary conditions and solve Eq. 4.11 analytically. However, this starts to get messy if we want more accurately to model the propagation of an action potential. In fact if we did the analysis more carefully we would not only ﬁnd that an action potential cannot propagate far along the cell, it also wouldn’t do so fast enough for nerve impulses.
A nerve cell cannot act like a wire and simply carry the electrical signal along it. As we have seen, cells are generally very leaky and a lot of the (ionic) current ﬂows out of the cell making them poor conductors. Instead the action potential mechanism itself is employed to achieve a net ﬂow of the signal down the nerve, where an action potential in one region causes another to ﬁre in the neighbouring region of the same cell, called active propagation: Fig. 4.5. An action potential at a point in the nerve cell causes a current of ions that means that the change in membrane potential extends along the cell. This leads to neighbouring regions of the cell reaching a potential above the threshold and thus also undergoing an action potential. In this case the action potential could propagate in either direction, in practice an action potential will be triggered at one end and propagate along.


<!-- ===== Page 65 ===== -->

4.4 Action Potential Propagation

53

Fig. 4.5. A schematic of active propagation

The speed of propagation varies between nerve cells and depends upon how far the effect of the action potential extends along the cell: the larger the region the more rapid propagation occurs. A larger region can be achieved either by reducing the resistance within the cell to the movement of ions, for example by making the cell diameter larger; or by increasing the resistance of the membrane, making it less leaky, so that more of the ionic current ﬂows along the cell. These are both methods to make the cable space constant in Eq. 4.11 larger.
Many vertebrate nerve cells insulate their nerve cells with a myelin sheath, as is the case for the neuron shown in Fig. 4.6. The disadvantage of this approach is that the action potential itself relies upon permeability of ions between the inside and outside of the cell. Thus very efﬁcient insulation would actually prevent an action potential from occurring and thus preventing propagation. This is avoided by having breaks in the myelin sheath, called nodes of Ranvier. The action potential thus effectively skips from one node to the next.

Fig. 4.6. Schematic of a nerve cell (neuron): the axon that carries the action potential is insulated with a myelin sheath, (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)


<!-- ===== Page 66 ===== -->

54
4.5 Conclusions

4 Cellular Transport and Communication

In this chapter we have looked at how substances can get in and out of the cell. You should now be able to identify and analyse some of the main mechanisms for transport across the cell membrane. We then looked at the related topic of how cells can communicate with each other. We concentrated on how an action potential can be passed from one cell to another and also how the action potential can propagate along a cell, so that we can achieve rapid signalling over a larger scale.


<!-- ===== Page 67 ===== -->

Chapter 5
Pharmacokinetics

We have already looked at the kinetics of reactions in Chap. 1, here we now consider how kinetic modelling can be applied to a whole ‘system’ such as an organ or the body as a whole. We will see that kinetic models and in particular compartmental models appear in various guises. To introduce the topic we are going to look at their use in pharmacokinetics.
Pharmacokinetics, often abbreviated to PK, is concerned with the fate of substances introduced into the body; most obviously this includes therapeutic agents, but might also include things like toxins. Pharmacokinetics is widely used to study substances in the whole body, for example where a drug has been delivered by injection and subsequently blood samples have been taken to determine the plasma concentration as a function of time. From these measurements we are interested in inferring what happened to the drug: how rapidly it was absorbed into tissues, how quickly it was removed from the body etc. However, pharmacokinetics also applies to various imaging modalities where some form of contrast agent is introduced and we want a spatially resolved map of absorption etc. We will revisit this when we look at Tracer Kinetics. Whilst pharmacokinetics follows what happens to the substance in the body it is also important to know what that substance is doing to the body, which is the aim of pharmacodynamics, but something that we will not consider here.

5.1 ADME Principles

Pharmacokinetics is commonly divided into a number of separate processes, referred to (for obvious reasons) as the ADME scheme, Fig. 5.1:
• Absorption is concerned with how the substance taken up into the blood stream or a speciﬁc tissue where it has been introduced.
• Distribution is concerned with how the substance is distributed throughout the body, most commonly how it goes from blood to tissue and back again.
• Metabolism is the conversion of the substance into other products usually via enzyme reactions.
• Excretion is the removal of the substance from the body, for example via the kidneys.

© Springer International Publishing Switzerland 2016

55

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_5


<!-- ===== Page 68 ===== -->

56

5 Pharmacokinetics

Fig. 5.1 ADME principles
The ﬁnal two processes together represent elimination, since they both result in the loss of the substance. In some cases we might also need to be concerned with liberation, the release of the substance we are interested in from the formulation that was used to introduce it. Most of these processes, particularly absorption and distribution, will involve some form of transport process to get the substance across membranes in the body. We have already looked at the various passive and active transport processes through which this might be achieved in Chap. 4.
5.2 Compartmental Models
Whilst there are a number of strategies for pharmacokinetics modelling we will follow the method of compartmental modelling. In this approach the substance is considered to be contained by and move between different compartments. These compartments are very broadly deﬁned and may not represent any speciﬁc part of the body, but rather a collection of tissues that share similar properties. The appeal of this method is that the model remains simple and we have some hope of using it to interpret the data; the disadvantage is that it can be harder to then interpret the model in terms of the underlying physiology.
5.2.1 One Compartment Model
We will start with the simple model shown in Fig. 5.2; in this case we have a single compartment into which the substance is absorbed and out of which it is eliminated. This is most likely to represent a substance in the blood plasma that is unable to cross into the tissues, thus we will talk about the concentration in this compartment as the plasma concentration. If we assume that a ﬁrst order output process describes


<!-- ===== Page 69 ===== -->

5.2 Compartmental Models

57

Fig. 5.2 One compartment model

the excretion with a constant ke then we can write a differential equation for the system, ignoring the input for the time being, as:

dCp ¼ ÀkeCpðtÞ; dt

ð5:1Þ

where Cp is the concentration in the compartment. If the substance were introduced by intravenous injection then we can deﬁne the input to the system via the initial conditions as the concentration at t = 0, i.e. Cp(0). Solving this equation gives a simple exponential decay for the plasma concentration:

CpðtÞ ¼ Cpð0ÞeÀket:

ð5:2Þ

Thus it would be possible to determine ke from data of Cp measured through blood sampling. From this we can also deﬁne the half-life of the substance as the time taken for 50 % of the substance to be eliminated: T1/2 = ln 2/ke. We might also be interested in the apparent volume of distribution for the compartment, which can be determined simply by dividing the dose given, D, by the initial concentration observed:

Vc ¼ D : Cpð0Þ

ð5:3Þ

This is the volume of the compartment into which the substance has distributed itself. We might assume in this case that this volume would equal the blood volume, since we have modelled the dug as only being in the blood. However, the volume of distribution is typically not equal to the blood volume, partially due to the drug only being in the blood plasma, thus not including the substantial volume occupied by blood cells. The volume of distribution allows us to deﬁne the total body clearance, the rate of elimination per unit of concentration:

Cltotal ¼ keVc:

ð5:4Þ

In the case of an intravenous injection it will actually take a short time from injection for the drug to have distributed throughout the whole circulation. Additionally, excretion will not begin until the substance has reached the right area


<!-- ===== Page 70 ===== -->

58

5 Pharmacokinetics

of the body. Thus Cp(0) will often be taken shortly after injection once a steady ‘initial’ condition should have been reached.
We can generalise our model for any arbitrary input as:

dCp ¼ ÀkeCpðtÞ þ CinðtÞ: dt

ð5:4Þ

It is also useful to write the equivalent expression for the total amount of the substance:

dAp ¼ Vc dCp ¼ ÀVckeCpðtÞ þ AinðtÞ;

dt

dt

ð5:5Þ

where A(t) = Vc C(t). This allows us to deal with the case of continuous intravascular infusion. Letting Ain(t) = k0 and solving for Cp:

CpðtÞ ¼ k0 À1 À eÀketÁ: Vcke

ð5:6Þ

From which we can determine the steady state concentration as t → ∞. Once again we can deﬁne T1/2: now it tells us how long it takes for 50 % of the steady state concentration to be reached, with the steady state being achieved after approximately 5 half-lives.
We can also derive the more general result:

CpðtÞ ¼ 1 Z Ain t ðkÞeÀkeðkÀtÞdk ¼ 1 AinðtÞ  eÀket;

Vc 0

Vc

ð5:7Þ

which you might recognise as a convolution as indicated by the  symbol on the right-hand side and thus the need for the dummy variable λ. Our model of instantaneous injection is thus equivalent to Ain(t) = D · δ(t), where δ(t) is the dirac
delta function. This allows us to consider more arbitrary intravenous introductions,
such as a series of injections or an infusion with a given duration.

Exercise A
(a) Starting with Eq. 5.5 derive the general result in Eq. 5.7. (b) Show that Eq. 5.6, for the plasma concentration during continuous
infusion, can be obtained from this result when Ain(t) = k0. (c) Determine the steady state concentration and consider the roles of k0 and
ke in reaching that steady state.


<!-- ===== Page 71 ===== -->

5.2 Compartmental Models

59

5.2.2 Absorption Compartment

So far we have considered only a ﬁrst-order output. However, the substance may have been administered orally, thus there is likely to have been at least one membrane for it to pass through to get into the plasma, requiring a ﬁrst order input, as in Fig. 5.3. Now we have two equations:

dAa ¼ ÀkaAaðtÞ þ AinðtÞ; dt dAp ¼ kaAaðtÞ À keApðtÞ; dt

ð5:8Þ ð5:9Þ

where we have introduced a new compartment with concentration Aa. Note that our convolution result above can be applied here. We could also write the equation for the amount of substance being eliminated:

dAe ¼ keApðtÞ; dt

ð5:10Þ

from which we could solve for Ae(t). This might be useful if we were able to make some direct measurements of elimination, for example urinary sampling.

Exercise B
(a) By modelling Ain as a Dirac delta function solve Eqs. 5.8 and 5.9 for plasma concentration Cp in response to a single oral dose.
(b) Sketch the result and comment on its shape. (c) If ka > ke comment on the shape of ln (Cp) as t → ∞. How might this be
used to estimate ke from plasma-sampled data?

Fig. 5.3 One compartment plus absorption model


<!-- ===== Page 72 ===== -->

60

5 Pharmacokinetics

Following Exercise B for a single oral dose of substance (Ain(t) = D · δ(t)) the plasma concentration can be written as:

CpðtÞ ¼ BD ka ÀeÀket À eÀkatÁ; Vc ka À ke

ð5:11Þ

where we have also included, B, the bioavailability of the substance. This is the fraction of the delivered dose that actually appears in the blood, taking into account losses in the gut through incomplete absorption and metabolism, as well as excretion in the liver. This can be calculated by comparing the area under the plasma concentration-time curve for oral delivery against the same dose of drug delivered intravenously.

Exercise C
The table below shows the measured plasma concentrations of a drug that was delivered by both intravenous injection and orally, with sufﬁcient time in between for the ﬁrst dose to wash-out completely. In both cases 2.0 g of agent were given.
(a) Calculate the bioavailability of the substance under oral administration. (b) Assuming ﬁrst order kinetics calculate the half-lives of elimination and
absorption. (c) Determine the volume of distribution for this drug.

IV injection Time (h) 0.10 0.25 0.5 0.75 1.00 1.50 2.00 3.00 5.00 7.00

Cp (mg/L) 190.2 176.5 155.8 137.5 121.3
94.5 73.6 44.6 16.4 6.0

Oral administration

Time (h) Cp (mg/L)

0.17

47.7

0.25

61.5

0.33

71.5

0.5

83.4

0.75

87.3

1.00

83.5

1.50

69.2

2.00

54.8

4.00

20.3

7.00

4.5


<!-- ===== Page 73 ===== -->

5.2 Compartmental Models

61

5.2.3 Peripheral Compartment

Finally (at least for our purposes) we will consider a substance that also exchanges from the plasma into the tissue: the distribution process. This requires us to add a further compartment to the model, Fig. 5.4. We still have a ‘central’ compartment, which includes plasma, but may also include tissues into which the substance rapidly exchanges (such that we are unable to distinguish them from plasma). We have gained a peripheral compartment, to where our drug is distributed, typically an organ or a collection thereof. This combination is generally called a two-compartment model; note that the absorption process is not counted as a compartment even though it behaves like one. The equation for the central compartment is now:

dAp ¼ kaAaðtÞ À keApðtÞ À k12ApðtÞ þ k21AgðtÞ; dt

ð5:12Þ

and the peripheral compartment:

dAg ¼ k12ApðtÞ À k21AgðtÞ: dt

ð5:13Þ

This can be solved reasonably easily for the simple cases of single dose and infusion that we have considered so far to give solutions for Cp that are sums of exponential terms.
Note that in pharmacological studies we generally have access only to the plasma compartment and have to try to determine all the unknowns of the system from that alone, which will be difﬁcult even with this relatively simple system.

5.2.4 Multi Compartment Models
We can build increasingly complex compartmental models if we need to include different peripheral compartments with differing rates of exchange, these will often
Fig. 5.4 Two compartment model (with absorption)


<!-- ===== Page 74 ===== -->

62

5 Pharmacokinetics

represent different organs (or groups of organs). The model might also need to account for the metabolism of the substance whilst in the tissue into various products (which may or may not then exchange back into the plasma). Metabolism is simply the result of a reaction, thus the reaction kinetics we saw in Chap. 1 can be applied and at their simplest match those we have been using here, which should not be a surprise since both are called kinetics. If the metabolic products do end up in the blood stream it might be possible to sample them too and thus to quantify more about the system.
A way to get around (or summarise) the complexity of a multi compartmental model is to return to the convolution expression we had earlier, but now to write the plasma concentration as:

CpðtÞ ¼ CinðtÞ  RðtÞ;

ð5:14Þ

where R(t) is the impulse response of the system (and gives rise to a transfer function in the Laplace or frequency domains). This impulse response function can be interpreted as the fraction of the substance that arrived at any point in time that is still present at some time later. By deﬁnition this impulse response function must start at unity at time zero and then monotonically decay.

5.2.5 Non-linear Models

So far all of the compartmental models have been linear. However, we have already met various non-linear processes in reactions and transport. Hence, if we were trying to build more physiologically accurate models we might need to incorporate some non-linear terms. The most common way to model non-linearities is using the Michaelis-Menten kinetics that we met in Chap. 1:

dCp ¼ À VmaxCp :

dt

Cp þ Km

ð5:15Þ

This can be regarded as pretty much ﬁrst order if Cp ≪ Km or zero order (saturated) if Cp ≫ Km.

Exercise D
A drug has been developed that is believed to be effective when the plasma concentration is greater than 20 mg/L, but toxic if the plasma concentration exceeds 100 mg/L.
The drug will be administered orally as a single dose D and is assumed to have ﬁrst order absorption as well as elimination kinetics.
(a) Identify the appropriate equation for the plasma concentration.


<!-- ===== Page 75 ===== -->

5.2 Compartmental Models

63

A clinical trial is about to begin and an appropriate dosing regime needs to be established. Initial experiments have determined the kinetic parameters for the drug in the table.
(b) Determine the maximum dose that can be delivered. (c) If the maximum dose is delivered, at what time would the plasma con-
centration no longer be sufﬁcient for the drug to be effective? (d) Subsequent study of the drug indicates that the elimination process occurs
via an enzyme-mediated process that is more accurately modelled by Michaelis-Menten kinetics with a constant Km = 2000 mg/L. Is the analysis performed in part (c) still valid?

Parameter F Vc ke ka

Value
0.8
10 L 0.0028 min−1 0.2 min−1

5.3 Tracer Kinetics
As we have seen pharmacokinetics sets out to describe the distribution of agents introduced into the body. Any quantitative measurements typically take the form of concentration samples taken from a speciﬁc compartment. With imaging devices it is possible to get spatially resolved measurements from inside the body, i.e. images. If we can introduce a contrast agent, or tracer, that will change the images, we could in principle measure the distribution of this agent. Two very common examples are Positron Emission Tomography (PET) and Magnetic Resonance Imaging (MRI).
In PET, a radioactive tracer is injected into the bloodstream; in principle any biologically compatible substance that can be radioactively labelled can be used. The most common is a sugar called F-18 labelled ﬂurodeoxyglucose (FDG), which behaves similarly to glucose, in that cells take it up. However, it then does not under go the subsequent (metabolic) reactions that glucose would and thus gradually accumulates in the organ of interest.
In MRI, the most common tracers are based on gadolinium, a material whose magnetic properties mean that its presence in tissues alters the image acquired using MRI in direct proportion to its concentration. MRI can also exploit blood water as a naturally occurring, or endogenous, tracer. This is most commonly applied in the brain and the magnetism of blood water is inverted in the neck prior to imaging in the brain. This process of Arterial Spin Labelling (ASL) allows the accumulation of


<!-- ===== Page 76 ===== -->

64

5 Pharmacokinetics

Fig. 5.5 Timeseries of ASL MRI tracer kinetics in the brain

labelled water to be observed in tissue, when it has had time to exchange from the blood into cells. In all of these imaging methods it is possible simply to take an image at the right moment, once enough of the contrast agent has accumulated, and to visualise the distribution of the agent. Alternatively it may be possible to acquire time series data of the agent as it is delivered and also removed, either by excretion from the cells or through physical decay of the agent signal. For example, the timeseries of the delivery labelled blood water into the brain using ASL MRI (along with the decay of the label) is shown in Fig 5.5.
The quantiﬁcation of delivery from imaging data is based on the principle of tracer kinetics, which is conceptually similar to pharmacokinetics. The contrast agent serves the same purpose as the drug in pharmacokinetics and we need a description of the input function to the tissue in the imaging region, commonly called the arterial input function. This can be obtained by blood sampling, more common in PET, or extracted directly from the images by looking at the time series in larger arteries, common in MRI.
Unlike pharmacokinetics, with imaging we have direct measures of the time series of our tracer in the tissue. Rather than getting a single series for a whole organ, we get measurements from each resolution element in the 3-dimensional imaging volume, called voxels. Thus for each voxel we have a time series for the tracer in that volume which will include both blood vessels and tissue. The form of this time series will depend upon what the tracer does when it gets to the tissue: for example, whether or not it all crosses the capillary wall and ends up in the cells or extra cellular space. The simplest case that we might adopt is the one compartment model, making the assumption that the tracer is eliminated according to a ﬁrst order process once it has arrived in the tissue. This is often a reasonable simpliﬁcation for FDG PET, ASL MRI and MRI using a Gadolinium contrast agent when imaging outside of the brain. The actual elimination process will be different in each case representing a combination of metabolism, exchange out of tissue back into the venous circulation and physical decay of the tracer itself. We can write the model for this process as:

dCt ¼ ÀkeCtðtÞ þ F Á CinðtÞ; dt

ð5:16Þ

where we are measuring the concentration of tracer in the tissue, Ct, we know from an independent measure the AIF, Cin, and we have a ﬁrst order elimination process with rate ke. Notice that the AIF is scaled by a parameter, F, which quantiﬁes the amount delivered. F has units of blood (carrying the agent) per volume of tissue per


<!-- ===== Page 77 ===== -->

5.3 Tracer Kinetics

65

unit time, this is in fact a quantify known as perfusion that we will meet again in Chap. 8. We could solve this equation for the function of Ct with time and use this to quantify perfusion from time series measurements. If we could provide an infusion of tracer we could simply acquire a single image once steady state has been reached to quantify perfusion. However, for various reasons infusion of the agent generally isn’t possible, often because the agent is toxic in too high a dose. For various PET tracers the elimination process is sufﬁciently slow that it is possible to use a single injection of tracer: the tracer accumulates and remains in the tissue and thus can be imaged sometime later for quantiﬁcation.
Like pharmacokinetics we can extend the model to more complex cases. For example, we can model what happens if there is a limiting rate at which the tracer leaves the blood into the extravascular space using a two compartment model. Tracer kinetics has a more general result that is applicable in a wide range of more complex tracer uptake situations:

CtðtÞ ¼ F Á CinðtÞ  RðtÞ:

ð5:17Þ

This is effectively a further generalisation of the convolution result we met in Eq. 5.14, where again we have an impulse response function R(t), in tracer kinetics this is often called the residue function. This function describes the fate of a unit of tracer once it has arrived in the voxel, whether it is washed out in the venous blood, is eliminated through metabolism, decays through some physical process etc. This function has special properties:
• Rðt ¼ 0Þ ¼ 1: this simply says that when a unit of tracer arrives it is all there; • Rðt [ 0Þ 1: this say that tracer either stays or is removed; • Rðt2Þ Rðt1Þ; t2 [ t1: this says that once tracer has been eliminated it cannot
come back again.
Notice that R(t) only tells us about a unit of tracer, strictly it tells us what happens to a (Dirac) delta of tracer that has arrived in the voxel. Thus Eq. 5.17 is modelling the voxel as a linear time invariant system with the AIF as the input. The observation that tracer accumulates in the voxel is thus a result of a delivery of tracer, described by the AIF, and that the tracer, once it has arrived, isn’t immediately removed from the voxel, as described by the residue function.
R(t) relates to the behaviour of the tracer in the voxel, and thus represents a property (or properties) of the volume of tissue in the voxel. Thus the shape of R (t) might be interesting in its own right in detecting tissue that is pathological, for example when looking for cancerous tissue. Hence, once we have time series data for each voxel we might try to extract R(t) either by writing it as a parameterised function and trying to estimate the parameter values from the data, or performing some form of numerical ‘deconvolution’.


<!-- ===== Page 78 ===== -->

66
5.4 Conclusions

5 Pharmacokinetics

In this chapter we have met a general method for the treatment of the body as a whole system in which the behaviour of substances can by described mathematically. You should now be able to use compartmental models built around the ADME principles to write down and to solve differential equations for simple pharmacokinetics problems. We have also seen how the same principles can be applied to measuring the delivery of a contrast agent to tissues, as is commonly used in medical imaging.


<!-- ===== Page 79 ===== -->

Chapter 6
Tissue Mechanics

6.1 Introduction
The model of the cell that we have been examining in Chaps. 1 and 2 provides a very neat link to models of tissue. At its simplest level, we can simply consider tissue to be a collection of cells, each of which behaves according to the rules that we set out in Chap. 2 (conservation of charge, equilibrium potential etc.). It turns out that we can use these rules to understand how tissue behaves at a larger scale. This then provides a good introduction to more general models of how tissue behaves as a material with properties such as Young’s modulus. We will concentrate on soft tissue, rather than bones and muscle: the main reason for this is that the deformations are larger and there is more interaction between ﬂuids and solids in soft tissue. Exactly the same principles can be applied to bones and muscle, but we will leave discussion of these to the many sources of information about this that can be found elsewhere.
6.2 Stress-Strain Relationships
Just like any material, human tissue must satisfy the conditions of equilibrium (where forces must balance) and compatibility (where the material must occupy all the available space). These two conditions can be written down in any suitable co-ordinate system, dependent upon the particular problem: we will restrict ourselves to Cartesian co-ordinates here. We will be using exactly the same equations as for any material, but we will see that tissue behaves in quite different ways to traditional engineering materials.

© Springer International Publishing Switzerland 2016

67

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_6


<!-- ===== Page 80 ===== -->

68

6 Tissue Mechanics

The equilibrium equations in three dimensions are:

@rx þ @sxy þ @sxz þ Fx ¼ 0 @x @y @z @ry þ @syx þ @syz þ Fy ¼ 0 @y @x @z @rz þ @szx þ @szy þ Fz ¼ 0 @z @x @y

ð6:1Þ ð6:2Þ ð6:3Þ

where the material has a body force per unit volume in each direction, Fx, Fy, Fz. We are using σ to denote direct stresses and τ to denote shear stresses and the
subscripts on the stresses indicate the direction of the force.
The strains are then related to the displacements as follows:

ex ¼ @u @x

ð6:4Þ

ey ¼ @v @y

ð6:5Þ

ez ¼ @w @z

ð6:6Þ

cxy ¼ @v þ @u @x @y

ð6:7Þ

cyz ¼ @w þ @v @y @z

ð6:8Þ

czx ¼ @u þ @w @z @x

ð6:9Þ

where we are using ε to denote direct strains and γ to denote shear strains. The
displacements are u, v and w in the x, y and z directions.
To solve these sets of equations, we need to relate stress and strain through the material properties of the tissue: for example using Young’s modulus (the ratio of stress to strain), E, and Poisson’s ratio (the ratio of strain perpendicular to applied force to strain in the direction of the applied force), ν. There are other material properties such as shear modulus, G, and bulk modulus, K, but these are all
inter-related. These material properties assume that the material is linear and iso-
tropic (i.e. the material properties are the same in every direction), which is far from the case for many tissues. We will think about this in more detail later, but let’s start
by looking at a linear material.


<!-- ===== Page 81 ===== -->

6.2 Stress-Strain Relationships

69

6.2.1 Linear Material

If the material can be assumed to be linear and isotropic, then the equations are just the same as those for any standard engineering material (such as steel). In this case strains in each direction are the sum of the direct and indirect strains:

ex ¼ 1 Àrx À mÀry þ rzÁÁ E
ey ¼ 1 Àry À mðrz þ rxÞÁ E
ez ¼ 1 Àrz À mÀrx þ ryÁÁ E

ð6:10Þ ð6:11Þ ð6:12Þ

Given suitable initial and boundary conditions, any stress and strain ﬁeld can be solved from this set of equations. A very simple example is given in Exercise A to solve a one-dimensional displacement problem for a soft tissue.

Exercise A

Consider a linear tissue where gravity is the only body force and it acts in the negative x direction.

(a) Assume: the problem is one-dimensional in the x direction; the material is of height L; the boundary conditions are zero displacement at x = 0 and zero stress at x = L. Show that the displacement of the tissue as a function of x is:

u ¼ qgx ðx À 2LÞ

ðA:1Þ

2E

(b) If the tissue has density the same as water and a value of Young’s

modulus of 500 Pa, calculate the displacement of the top of the tissue if it is 1 cm tall (for convenience take g = 10 m/s2).

You will ﬁnd that the displacement is surprisingly large (approximately 1 mm for a tissue of height 1 cm). This is because the value of Young’s modulus is very
small compared to the kind of values that you may be used to for more common engineering materials (for example, steel has a Young’s modulus of around
200 GPa). Soft tissue is inherently very deformable, as you might expect.


<!-- ===== Page 82 ===== -->

70
6.2.2 Non-linear Material

6 Tissue Mechanics

Of course many tissues are neither linear nor isotropic: this introduces additional complexity. As we showed in the previous section, human tissue is also not very stiff, which means that the usual assumption of small displacements is no longer valid. The theory behind tissue movement is thus more complex, because we have to consider two frames of reference.
We won’t consider non-isotropic behaviour here, but we will look very brieﬂy at non-linear behaviour. A very common equation for modelling soft tissue is that proposed by Fung, based on the idea of strain energy density, W. The strain energy density function is just the amount of energy stored in the material per unit volume due to strain. The advantage of writing down the strain energy density is that it provides a single representation of the stress-strain relationship, from which individual stress and strain terms can be calculated. For a linear isotropic material (such as might be assumed for steel or aluminium, for example) with only direct stresses, this would be:

W ¼ 1 E e 2x þ e2y þ e2z  2

ð6:13Þ

Individual stress terms are calculated by differentiating Eq. (6.13) with respect to individual strain terms, for example:

rx ¼ @W ¼ Eex @ex

ð6:14Þ

hence Young’s modulus. This is the simplest example and anything else becomes very complicated very quickly. However, we can extend the linear isotropic material to a non-linear isotropic material by adapting the strain energy density function to give:

W ¼ 1 a k h À 2 þ k2 þ k2 À 3Á þ c e  bðk12 þ k22 þ k32À3Þ À 1i 2 123

ð6:15Þ

The terms λi refer to the principal strains, which are simply the ratios of the new ‘lengths’ of an element to the original ‘lengths’ in each direction and thus directly
related to strain. The constants a, b and c are set to match experimental data. The Fung expression above then models the fact that at small strains, the Young’s
modulus of tissue is very small (the ﬁrst term), but that as the strain increases, the effective Young’s modulus increases very rapidly (the second, exponential, term).
Again, we can use these results to derive relationships for stress and strain, but these are quite complicated in comparison with the linear model, so we won’t go
any further here. We will, however, explore some examples where tissue interacts
with other substances in non-linear ways to show how we can use stress and strain


<!-- ===== Page 83 ===== -->

6.2 Stress-Strain Relationships

71

to model soft tissue. This will illustrate how we have to consider tissue mechanics very differently to more traditional engineering mechanics.

6.3 Coupled Cell-Tissue Model

We start by going back to our model of the cell from earlier chapters. Consider a simple cell surrounded by a solution. The cell has both positive and negative ions inside, with concentrations c+ and c− respectively, and the extracellular space has a concentration c*. The resulting pressure is proportional to the difference in internal and external concentrations:

p ¼ RTððc þ þ cÀÞ À cÃÞ

ð6:16Þ

where R and T are the ideal gas constant and absolute temperature respectively. This is just like the ideal gas equation, with concentration replacing density.
In Chap. 2, we noted that the inside of the cell possesses a certain amount of ﬁxed charge, attached to proteins that cannot move across the cell membrane (unlike the ions, which can move through channels). The intracellular concentrations can be written in terms of the extracellular and ﬁxed charge concentrations:

qﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ c þ þ cÀ ¼ ðcÃ2 þ c f 2 Þ

ð6:17Þ

Of course the ﬁxed concentration, cf, varies with the size of the cell, since it is the total charge that is ﬁxed, and so concentration varies inversely with cell volume. We can relate this to the expansion or contraction of the tissue:

cf ¼

! /0 f w
c0 dVV þ /w0

ð6:18Þ

where /0w is the tissue water content in some baseline state. This then gives a scaling for the ‘new’ volume of the cell as a fraction of the ‘original’ volume: to calculate this we need to deﬁne how the cell volume responds to pressure. This requires a model of the tissue, as we examined earlier.
The very simplest model is to assume that displacements are (at least relatively) small and that an applied pressure gives rise to a strain. This is based on the deﬁnition of bulk modulus (K):

K ¼ ÀV dp dV

ð6:19Þ


<!-- ===== Page 84 ===== -->

72

6 Tissue Mechanics

The volume change will be:

dV ¼ ð1 þ eÞ3À1 V

ð6:20Þ

If the strain is small, then we can approximate this by:

dV ¼ 3e V

ð6:21Þ

Hence, using Eq. 6.19:

p ¼ 3Ke

ð6:22Þ

The factor of 3 essentially comes from the fact that tissue is three-dimensional and so the volume change is approximately three times the strain in each separate dimension.
In its simplest form, we can combine all of the equations above to give:

0v0ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ1ﬃﬃﬃﬃ 1

u

!2

u

wf

3Ke ¼ RTB@u t@cÃ2 þ

/0 c0 A ÃC w Àc A

3e þ /0

ð6:23Þ

This gives a relationship between tissue strain and extracellular concentration (we can calculate the pressure from the strain). Note that it is not a straightforward expression to solve (although it can be written in simpler form, as in Exercise B): it is also strongly non-linear. These are both common features of models derived from physiological systems and we often require numerical methods to solve the equations and models that we derive. This does, however, give many interesting types of behaviour.

Exercise B

(a) Show that Eq. (6.23) can be re-written in the form:

cÃ ¼ RT 2p

w f !2

/0 c0

p

p wÀ

k þ /0

2RT

relating concentration to pressure. (b) Comment on the form of this relationship.

ðB:1Þ


<!-- ===== Page 85 ===== -->

6.4 Coupled Fluid-Tissue Model

73

6.4 Coupled Fluid-Tissue Model

Having considered a very simple model relating cellular behaviour to tissue behaviour, let’s now consider the interaction between tissue and ﬂuid more rigorously. This ﬂuid could be water or blood in very small blood vessels. It is not possible to model individual pores or blood vessels, except on a very small scale, so we have to consider an alternative way of describing this. The most common way of doing this is to use the idea of a porous medium. This is a concept that is very familiar in soil mechanics, where it is used to describe the drainage of soils with water content.
The early work on soil consolidation (the fact that loading a soil results in a gradual settlement of that soil when it is saturated with water) was performed by Terzaghi in the 1920s and developed further by Biot in the 1940s. The theory builds upon elastic continua theory with the addition of an expression for increment of water content, θ, as a function of stress and water pressure:

h ¼ 1 Àrx þ ry þ rzÁ þ p

3H

R

ð6:24Þ

where H and R are physical constants. For a linear material, the stresses are related to strains through Hooke’s law:

ex ¼ 1 Àrx À mry À mrzÁ þ p

E

3H

ey ¼ 1 Àry À mrx À mrzÁ þ p

E

3H

ez ¼ 1 Àrz À mrx À mryÁ þ p

E

3H

ð6:25Þ ð6:26Þ ð6:27Þ

Hence:

h ¼ ae þ p Q

ð6:28Þ

where:

e ¼ ex þ ey þ ez

ð6:29Þ

is now deﬁned as the total volumetric strain and:

a ¼ 2ð1 þ mÞG 3ð1 À 2mÞH

ð6:30Þ


<!-- ===== Page 86 ===== -->

74

6 Tissue Mechanics

1 ¼1Àa Q RH

ð6:31Þ

The water content is thus dependent upon the total volumetric strain and the
water pressure in a linear way, with the coefﬁcients dependent upon the material
properties of the tissue. The ﬂow of a ﬂuid through a porous medium is then normally governed by
Darcy’s law, which is again very commonly found in civil engineering:

q ¼ À j rp l

ð6:32Þ

In this equation, q is the vector ﬂow rate per unit area (so it has the dimensions of m/s), and κ and μ are the permeability of the porous medium and the viscosity of the ﬂuid respectively. Essentially this equation just says that ﬂow moves down a
pressure gradient, with this being proportional to how easily it can pass through the porous medium and inversely proportional to the ﬂuid viscosity.
To solve this equation, we will consider the ﬂuid to be incompressible, which is
in fact a very good approximation since blood is largely composed of water, which
is essentially incompressible. In this case, conservation of volume gives:

@h ¼ Àr Á q @t Equations 6.28, 6.32 and 6.33 can be combined to give:

ð6:33Þ

j r2p ¼ a @e þ 1 @p

l

@t Q @t

ð6:34Þ

which is the equation governing the ﬂuid; the only thing remaining is the relationship between pressure and strain for the solid matrix. In this context these can be written down as:

Gr2u þ G 1 À 2m r Á e ¼ ar Á p

ð6:35Þ

These come from the equilibrium equations and the statement of Hooke’s law above. Solving these equations then just requires a set of initial and boundary conditions and a suitable numerical solver.


<!-- ===== Page 87 ===== -->

6.4 Coupled Fluid-Tissue Model

75

Exercise C
(a) Consider a porous medium in one dimension. Show that the governing equation for pressure is of the form:

@2p ¼ 1 @p @x2 c @t

ðC:1Þ

and derive an expression for the coefﬁcient, c. (b) Consider a material occupying the positive x line, such that the boundary
is at x = 0 and the material extends inﬁnitely in the positive x direction. Initially the pressure is zero throughout, but at time t = 0, a step change in pressure of magnitude P is applied at the boundary. Calculate the pressure in the material as a function of distance and time.

The result in Exercise C is very similar to the heat equation that governs the ﬂow of heat in a one-dimensional passive material. Solutions to this partial differential equation are very standard and importantly are only dependent upon one parameter, as shown in the exercise. This means that they are well understood and can be applied relatively easily, although of course we are assuming linear and isotropic behaviour, so it does become much more challenging if this is not the case.

6.5 Coupled Blood Vessel-Tissue Model

As well as considering tissue as a continuum, we might also want to describe how it interacts with blood ﬂow in individual vessels, i.e. on a larger scale. There is here a strong interaction between the ﬂuid and the structure due to the fact that the ﬂuid
has a variable pressure. This is very similar to the theory of thin-walled and
thick-walled vessels, used widely in standard pressure vessel theory, for example. Note that we will be changing from x-y-z co-ordinates to r-θ-z co-ordinates.
Let’s start by considering a thick cylinder under uniform pressure as our model
of a blood vessel. The radial and circumferential stresses are given by:

B rr ¼ A þ 2
r

ð6:36Þ

B rh ¼ A À 2
r

ð6:37Þ

where A and B are constants, set by the boundary conditions. Note that these come
from solving the equilibrium and compatibility equations in cylindrical polar co-ordinates (these are standard results, so we won’t derive them here).


<!-- ===== Page 88 ===== -->

76

6 Tissue Mechanics

If we assume that we have a blood vessel with blood at a uniform pressure p inside it and pext outside it, these equations turn into:

pR2 À pextðR þ hÞ2 þ R2ðR þ hÞ2ðpext À pÞ=r2

rr ¼

22

ðR þ hÞ ÀR

ð6:38Þ

pR2 À pextðR þ hÞ2ÀR2ðR þ hÞ2ðpext À pÞ=r2

rh ¼

22

ðR þ hÞ ÀR

ð6:39Þ

where the wall has thickness h and inner radius R.

Exercise D
Show that the expression in Eq. 6.38 is compatible with the pressure boundary conditions.

At this point, we need to make an assumption about the stress or strain in the
axial direction to calculate the displacements. There are two very common choices:
plane stress (where the stress in the axial direction is zero) or plane strain (where the strain in the axial direction is zero). We will consider these brieﬂy in turn.

6.5.1 Plane Stress

In the ﬁrst case, there is no stress in the axial direction and the vessel is allowed to expand in this direction as it wishes. The circumferential strain in cylindrical polar co-ordinates is given by:

eh ¼ u ¼ 1 ðrh À mrrÞ rE

ð6:40Þ

where the material typically has a Poisson’s ratio, ν, of 0.5 (the value for an incompressible material). Substituting the expressions for stress into this equation at the inner radius then gives the internal displacement of the vessel wall. The resulting expression is long and complicated, so we won’t quote it here; however, the main thing to note is that the displacement is linearly proportional to both the internal and the external pressure. This should be no surprise, since we assumed a linear material; however, it does still illustrate that even with these simple assumptions the ﬁnal expression can be highly complicated.


<!-- ===== Page 89 ===== -->

6.5 Coupled Blood Vessel-Tissue Model

77

6.5.2 Plane Strain

In the second case, there is no strain in the axial direction and the vessel is constrained to expand only in the radial direction. The circumferential strain in cylindrical polar co-ordinates is thus:

u ð1 À m2Þ 

m

eh ¼ ¼

rh À

rr

r

E

1Àm

ð6:41Þ

Substituting the expressions for stress into this equation again gives a linear relationship between pressures and wall displacement, but with different coefﬁcients (it can be shown that the plane stress condition gives a smaller displacement than that for plane strain for the same applied internal pressure).
Having derived this result, we can simply say that both assumptions yield the result that displacement is proportional to pressure. Since the vessel wall inner radius is not zero at zero pressure, we introduce an offset and turn the expression into the form:

R À Ro p À po ¼ Go Ro

ð6:42Þ

where we deﬁne the wall stiffness as Go and the vessel wall has radius Ro at pressure po. Notice that we are slightly abusing our notation to write R as the variable inner wall radius now (i.e. equal to the original radius plus the displace-
ment). This allows us to relate the pressure inside the vessel to the wall radius. The pressure inside the blood vessel will be determined by the ﬂow of blood in
the vessel, so, having considered the relationship between wall displacement and applied pressure, we turn to the governing equations for ﬂow inside the vessel.
We start by assuming an axisymmetric straight vessel and write down the
equations for continuity and momentum as:

@A þ @ðAUÞ ¼ 0 @t @x

ð6:43Þ

@U þ U @U ¼ À 1 @p þ f

@t

@x

q @x qA

ð6:44Þ

where the vessel has cross-sectional area A, and the ﬂuid has average velocity U, pressure p and density ρ. f denotes the friction term caused by the viscosity of the ﬂuid. The ﬁrst equation (continuity) balances the storage of ﬂuid due to changes in cross-sectional area with the rate of change of ﬂow along the vessel. The second
equation can be thought of as an application of Bernoulli’s equation with an added term for the friction of the ﬂuid (this is what dissipates energy in a real ﬂuid).


<!-- ===== Page 90 ===== -->

78

6 Tissue Mechanics

Note that there are four variables in these two equations: we therefore need two
more equations. We can calculate the frictional force if we estimate the velocity proﬁle of the ﬂuid through the vessel: it is normal to guess a polynomial proﬁle, as
you will see in Exercise E.

Exercise E

Assume that the velocity of the ﬂuid through a blood vessel is of the form:

  r n uðrÞ ¼ Umax 1 À R

ðE:1Þ

(a) Show that the mean ﬂow velocity, averaged over the cross-sectional area, is given by:

 U ¼ Umax n
nþ2

ðE:2Þ

(b) Hence show that the frictional force per unit length of the vessel is given by:

f ¼ À2plðn þ 2ÞU

ðE:3Þ

This result means that we have just three variables remaining. The usual way to complete this set of equations is to consider the relationship between the ﬂuid
pressure and the vessel wall area, along the lines that we derived earlier. Re-writing
Eq. 6.42 in terms of vessel area gives:

rﬃﬃﬃﬃﬃ  p À po ¼ Go A À 1
Ao

ð6:45Þ

The governing equations can thus be written as:

@A þ @Q ¼ 0 @t @x

 2

rﬃﬃﬃﬃﬃ

@Q @ Q Go A @A

2plðn þ 2ÞQ

þ

þ

¼À

@t @x A 2q Ao @x

qA

ð6:46Þ ð6:47Þ

where we are writing them in terms of area and ﬂow rate (deﬁned as Q = UA), rather than area and velocity.


<!-- ===== Page 91 ===== -->

6.5 Coupled Blood Vessel-Tissue Model

79

Now that we have two simultaneous equations, we can examine how they behave. You will notice that they are very similar in form and so it is common to write them in vector/matrix form:

@U þ HðUÞ @U ¼ BðUÞ

@t

@x

ð6:48Þ

where:

! U¼ A
Q

" 0 qﬃﬃﬃﬃ
HðUÞ ¼ Q2 Go A À A2 þ 2q Ao

# 1 2 AQ

"

#

0

BðUÞ ¼ À qA 2plðn þ 2ÞQ

ð6:49Þ ð6:50Þ ð6:51Þ

These are called the quasi-linear matrix form of the equations and might remind

you of the wave equation. The eigenvalues of H(U) can be shown to be the mean ﬂow speed plus or minus the wave speed, and are given by:

sﬃﬃﬃﬃﬃ 1 k ¼ Q Æ Go A 4
A 2q Ao

ð6:52Þ

The ﬁrst term is the mean speed of the ﬂuid and the second term is the wave speed. Any disturbance in the ﬂow (such as a pulse of blood) will thus cause a movement both forwards and backwards. This movement will have a speed that is proportional to the square root of the vessel wall stiffness: hence in very stiff vessels, the wave speed is very high. Typical values are that the vessel wall stiffness is of order 10 kPa and the density of blood is about 1000 kg/m3, so the wave speed is a few metres per second.
In the limit as the vessel walls become inﬁnitely stiff, the pulse wave speed tends to inﬁnity and we can get shock waves forming. This is one of the reasons why cardiovascular problems develop with age, as vessel walls become stiffer (for example as the result of fatty deposits on the vessel wall). The wave speed will also be higher when the vessel is dilated, i.e. when the pressure is higher, but this is a smaller effect.

6.6 Conclusions
In this Chapter, we have examined ways in which we can model both tissue and its interaction with cells, water and blood. The key idea of the chapter is the fact that there is this interaction between difference components of body organs: they cannot


<!-- ===== Page 92 ===== -->

80

6 Tissue Mechanics

be considered in isolation, as for many other engineering problems. This does make the task of understanding their behaviour very complicated and we have only examined a few very simple cases to give you the idea of what can be done in this ﬁeld. There are very many other examples that you will be able to ﬁnd elsewhere.


<!-- ===== Page 93 ===== -->

Chapter 7
Cardiovascular System I: The Heart

7.1 Overview
The cardiovascular system, which is also known as the circulatory system, comprises the human heart, blood vessels and blood. It has ﬁve main functions:
1. Distribution of O2 and nutrients, for example glucose and amino acids, to all body tissues;
2. Transport of CO2 and metabolic waste products from the tissues to the lungs and other excretory organs;
3. Distribution of water, electrolytes and hormones throughout the body; 4. Contributing to the infrastructure of the immune system; 5. Thermoregulation.
Its overall aim is to maintain the body within well-deﬁned limits, irrespective of external stimuli: this equilibrium is termed homeostasis.
A schematic outline of the system is shown in Fig. 7.1 with the heart at the middle. Although it looks complicated, it is actually relatively simple: the blood ﬂows in a continuous loop, from the right ventricle to the lungs (where carbon dioxide in the blood is removed and exchanged for oxygen), to the left atrium and left ventricle, out to the body tissues (where oxygen passes into the tissue in exchange for carbon dioxide) and back into the right atrium and ventricle. If you get lost, try tracing your ﬁnger around a path until you get back to where you started from.
Note that, although the lungs are a single entity, the remainder of the body tissues are very widely spread out. The main body tissues in descending order of blood ﬂow rate are shown in Table 7.1. The circulation is sometimes divided into pulmonary and systemic components, where the pulmonary circulation comprises the lungs and the systemic circulation all the body tissues.

© Springer International Publishing Switzerland 2016

81

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_7


<!-- ===== Page 94 ===== -->

82

7 Cardiovascular System I: The Heart

Fig. 7.1. Structure of cardiovascular system and heart. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/

Table 7.1 Distribution of blood between body organs, in descending order

Kidney Spleen Skeletal muscle Brain Liver Skin Bone Heart muscle

22 % 21 % 15 %

14 % 6 % 6 % 5 % 3 %

Other 8%


<!-- ===== Page 95 ===== -->

7.2 Structure and Operation of the Heart

83

7.2 Structure and Operation of the Heart

The most important part of the system is the heart, which acts as the pump driving blood round the body. The heart is divided into two sections, left and right: the left side pumps oxygenated blood from the lungs to the tissues, whilst the right side pumps de-oxygenated blood from the tissues back to the lungs. A healthy adult heart pumps approximately 5 L of blood around the body every minute. Over the course of a 70-year life span, a heart will beat several billion times and deliver over 100 million litres of blood.
A schematic of the structure of the heart is shown in Fig. 7.1. Although it looks complex, again it is relatively straightforward. The main division is into the left and right sides (confusingly pictures of the heart are normally shown as looking front on, whereas left and right are deﬁned as per the person’s left and right). They are also normally coloured in red and blue respectively since de-oxygenated blood is blue and oxygenated blood is red.
Both sides are subdivided into an atrium and a ventricle: there are thus four chambers in total. The two atria are thin-walled and receive blood from the veins (pulmonary veins on the left side and superior and inferior vena cava on the right side), whereas the two ventricles are thick-walled and pump blood out through the arteries (aorta on the left side and pulmonary arteries on the right side). Note how the aorta is arched as the blood comes out of the top of the left ventricle upwards but then goes downwards (the small vessels coming off the top of this arch supply the brain and cardiac muscle).
There are also four valves: one at the exit from each chamber. The mitral and aortic valves are found on the left side at exit from the atrium and ventricle respectively; the tricuspid and pulmonary valves on the right side similarly. The two valves at exit from the ventricles are semilunar valves with three cusps, i.e. three semicircles that act to cover the cross sectional area, whereas the mitral and tricuspid valves have inextensible ﬁne chords (chordae tendineae) extending from free margins of the cusps to the papillary muscles, which contract during systole, thus acting somewhat like parachutes.
The heart wall is comprised of three layers, as shown in Fig. 7.2: the epicardium, myocardium and endocardium, from outer to inner. The endocardium is a thin layer of cells, similar to the endothelium found in blood vessels; the myocardium is the muscle and the epicardium is the outer layer of cells. The whole heart is contained within the pericardium, a thin ﬁbrous sheath or sac, which prevents excessive enlargement. The pericardial space contains interstitial ﬂuid as a lubricant.
The cardiac cycle comprises two parts: the resting (or ﬁlling) phase, termed diastole, and the contractile (or pumping) phase, termed systole. During the ﬁrst phase, blood enters the heart on both sides simultaneously through the veins. The pulmonary and aortic valves are both shut, so the atria and ventricles expand. During the second phase, the heart contracts strongly and the pulmonary and aortic valves open: a pulse of blood thus ﬂows out into the pulmonary arteries and aorta. However, it is important to remember that blood is still ﬂowing in through the


<!-- ===== Page 96 ===== -->

84

7 Cardiovascular System I: The Heart

Fig. 7.2. Structure of heart wall. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/
veins: the heart must accept this blood and make sure that blood is not forced back into the veins at any point in the cycle.
This is when the separate chambers become important: the tricuspid and mitral valves are shut automatically by the pressure that builds up in the ventricles and so the atria continue to receive blood whilst it is being forced out of the ventricles. The structure of the tricuspid and mitral valves is the reason for this unidirectional behaviour, since they are attached to the ventricular walls and thus permit ﬂow through in one direction only, as shown in Fig. 7.1. Similarly, when the ventricles relax, the pulmonary and aortic valves act to prevent blood from ﬂowing back into the ventricles: these valves are thus also unidirectional.
Note that the heart valves behave in a very similar way to electrical diodes, where the current can only ﬂow one way. In fact there is always some leakage in the heart valve, just as there is in a diode, but as long as this doesn’t get too large, it can safely be ignored. The structure of the heart thus enables it to receive a constant ﬂow of blood through the veins, whilst pumping out blood at regular intervals through the arteries. It is important to remember that the body receives a pulsatile, rather than a steady, ﬂow of blood, although this pulsatile ﬂow is smoothed out rapidly as the blood passes into the vasculature.
The myocardium is the muscle in the heart wall whereby the heart contracts and obviously it must be supplied with blood to function properly. The cardiac muscle has a network of blood vessels to supply it, via the left and right coronary arteries, which branch off the ascending aorta. After passing through the myocardium these vessels feed back to the right atrium via the coronary sinus. The operation of the coronary system is thus vital in maintaining continuous blood supply to the heart muscle.


<!-- ===== Page 97 ===== -->

7.2 Structure and Operation of the Heart

85

Ischaemic (meaning a reduction in blood supply) heart disease is caused by an imbalance between the blood ﬂow to the myocardium and the myocardial metabolic demand. If the coronary arteries block up (through deposits of fatty substances on the wall), their resistance to ﬂow increases, reducing the supply of blood. A myocardial infarction (the technical term for a heart attack) means that some of the heart muscle cells die due to this lack of blood supply. This death can cause irregular rhythms, which can be fatal even if there is enough healthy muscle to continue pumping.
After myocardial infarction, the heart can recover, although it will rarely be able to pump as much or as efﬁciently as before. Nowadays, most patients survive heart attacks, due to rapid treatment, and bypass operations, which open up the blood supply, can reduce the chance of a future heart attack. The heart obviously plays a crucial role in the operation of the human body: if it stops operating for even a very short time, the build-up of waste products and starvation of nutrients leads rapidly to irreversible cell death.

7.3 Measurement of Cardiac Output

Given the key role of the heart in the operation of the human body, it is obviously important to be able to monitor its behaviour. We will look at a number of ways, but the ﬁrst one that we will examine is termed Cardiac Output (CO): this is simply the rate at which the heart pumps blood out into the pulmonary and systemic circulations. There are a variety of ways to measure CO, both directly and indirectly.
The ﬁrst technique is based on Fick’s principle, which simply equates the absorption of oxygen in the capillaries to the oxygen inhaled in the lungs (effectively balancing the input and output of oxygen in the body). The absorption of oxygen in the capillaries can be calculated as the difference between the oxygen contents in the arteries and the veins: these are normally measured in units of ml_O2/ml_blood. The oxygen consumption of the body, measured in ml_O2/min, is the product of this difference and the CO, measured in ml_blood/min: we are essentially using oxygen as a tracer. CO can thus be calculated by:

CO ¼ VO2 ðO2arterial À O2venousÞ

ð7:1Þ

Indicator dilution techniques are based on the idea that if a known amount of a substance is injected into an unknown volume, the ﬁnal concentration allows the volume to be calculated. In Hamilton’s dye method a quantity of non-toxic dye is injected into a vein: it mixes with the blood as it passes through the heart and lungs. By taking successive arterial blood samples, the mean concentration can be calculated. Cardiac output is then calculated from:


<!-- ===== Page 98 ===== -->

86

7 Cardiovascular System I: The Heart

CO ¼ ADI MDC Á DFP

ð7:2Þ

i.e. the ratio of the Amount of Dye Injected (ADI) to the product of the Mean Dye Concentration (MDC) with Duration of First Passage (DFP).
A variant on this is the thermodilution technique, which is the most common method to measure CO. A modiﬁed Swan-Ganz catheter with a thermistor at its tip and an opening a few centimetres from the tip is inserted from a peripheral vein such that the tip is in the pulmonary artery and the opening is in the right atrium. A small amount of cold saline is injected into the atrium and this mixes with the blood as it passes through the ventricle and into the pulmonary artery, thus cooling the blood. By measuring the blood temperature, the ﬂow rate can be calculated, since the temperature drop is inversely proportional to the blood ﬂow. This is very similar to the indicator dilution technique, but measuring the dilution of temperature rather than concentration.
More modern non-invasive techniques (i.e. those that do not require the insertion of any probes into the body) use imaging methods to estimate real-time changes in the size of the ventricles. This can be used to give the Stroke Volume (SV): the volume of blood pumped out in one cardiac cycle. The CO can then be calculated, using a simultaneous measurement of the heart rate (HR), from:

CO ¼ SV Á HR

ð7:3Þ

Imaging methods, like MRI, have the potential for great accuracy and for beat-to-beat measures of CO, but are of course very much more expensive and difﬁcult to use, despite being non-invasive in nature.

Exercise A
Calculate cardiac output if oxygen consumption is calculated to be 200 ml_O2/min and arterial and venous oxygen concentrations are 0.21 and 0.16 ml_O2/ml_blood. If the heart rate is 60 beats per minute, calculate the stroke volume. Comment on your answer.

7.4 Electrical Activity of the Heart
Thus far, we have simply considered the mechanical activity of the heart, by looking at it as a pump and thinking in terms of blood ﬂow. We will now look at the electrical activity of the heart, considering what drives it, in particular what makes it expand and contract, before looking at how we can monitor its performance. This builds upon Chap. 3, where we looked at the generation of the action potential.


<!-- ===== Page 99 ===== -->

7.4 Electrical Activity of the Heart

87

7.4.1 The Action Potential

The action potential of a cardiac muscle cell, as shown in Fig. 7.3a, is similar to that of the cells that we examined earlier, but with the addition of a sustained plateau due to the inﬂuence of Ca2+. Calcium ions play a very important role in cardiac cells.
Depolarization: This is the ﬁrst phase of cardiac cell ﬁring: this lasts approximately 2 ms. As in the example shown in Chap. 3, the action potential is generated by a sudden transient rise in Na+ permeability with a subsequent increase in potassium permeability (remember the m, n and h gates). The inward current of Na+ ions through voltage-gated Na+ channels becomes sufﬁciently large to overcome the outward current through K+ channels and so the cell potential increases (becomes less negative): the membrane thus suddenly becomes much more permeable to Na+ ions due to the channels. This process then activates more Na+ channels and the process becomes self-perpetuating (essentially there is positive feedback and the system is unstable).
Plateau: The role of calcium now becomes crucially important. When the membrane potential reaches a threshold, voltage-dependent calcium channels open and there is a large inﬂux of calcium ions. There are also some potassium channels that close upon depolarization (the opposite to the potassium channels discussed in Chap. 3). These two effects contribute to the plateau, where the membrane potential decays only very slowly over approximately 200 ms, even though the sodium permeability returns virtually to its resting value.
Repolarization: The next stage is a more rapid drop. This is due to a gradual decline in the calcium permeability and an increase in potassium permeability. The precise mechanisms are still not fully understood, but the decline in calcium permeability may be due to the effect on the calcium channels of the accumulation of calcium in the cells. By the end of this phase, the outward potassium current returns to its dominant position and the membrane potential returns to its resting value before the next action potential begins.
Since the action potential automatically causes a mechanical response, with the tissue contracting and becoming shorter in length, it might be wondered why there is a need for a more complicated action potential. This is because in cardiac muscle, the duration and strength of the contraction are important parameters that will have to be adjusted dependent upon the circumstances: more control is needed over the action potential and this is achieved through the use of calcium ions. This is shown in Fig. 7.3b, where the prolonged action potential results in a more powerful contraction: calcium ions thus give a lot of control over the magnitude of the tensile forces.


<!-- ===== Page 100 ===== -->

88

7 Cardiovascular System I: The Heart

Fig. 7.3. Action potential in cardiac muscle cells: a electrical activity; b electrical and tensile behaviour. This ﬁgure is taken, without changes, from OpenStax College under license: http:// creativecommons.org/licenses/by/3.0/
7.4.2 Pacemaker Potential
Heart cells in isolation beat rhythmically, i.e. they exhibit a spontaneous action potential that does not require an external stimulus to start the process, thus they do not have a true resting potential. Like skeletal muscle, the cardiac action potential has a phase where the open potassium channels slowly close (this was the ‘undershoot’ for the earlier action potential). As the system returns to ‘baseline’ the threshold is once again reached for depolarization and the whole process restarts.


<!-- ===== Page 101 ===== -->

7.4 Electrical Activity of the Heart

89

This is referred to as the pacemaker potential. In reality the rate of action potentials in cardiac muscle cells varies from cell to cell and thus there needs to be some form of co-ordination to ensure that the whole muscle contracts simultaneously.

7.4.3 Cardiac Cycle
The stimulus for the cardiac action potential is provided by the SinoAtrial Node (SAN): the cells found in the SAN are often termed pacemaker cells. It has an unstable resting potential, as shown in Fig. 7.4, which decays from approximately −60 mV to a threshold value of −40 mV, at which an action potential is initiated. The rate of decay of this resting potential thus determines the rate of ﬁring and hence the heart rate. In a healthy human at rest, this will result in action potentials being started approximately 70–80 times each minute.
As the SAN cells depolarise, they stimulate the adjacent atrial cells, causing them to depolarise similarly. The depolarisation wave spreads over the atria in an outward-travelling wave from the point of origin, the action potential passing from cell to cell via electrical synapses, as described in Chap. 4. Both atria contract nearly simultaneously, as do both ventricles shortly afterwards. Co-ordination between atria and ventricles is achieved by specialised cardiac muscle cells that make up the conduction system, as shown in Fig. 7.5.
The wave is prevented from spreading past the limits of the atria by a ﬁbrous barrier of non-excitable cells: the only excitable tissue that crosses this barrier is the Bundle of His. At the origin of this bundle is a mass of specialised tissue about 2 cm long and 1 cm wide called the AtrioVentricular Node (AVN). The conduction velocity through the AVN is approximately 0.1 m/s, some 10 % of that of the atrial cells. The delay that this causes is vital in preventing the ventricles from contracting before the atria have completed their contraction. The impulse from the AVN travels through the Bundle of His, which splits into the left and right bundle

Fig. 7.4. Action potential at the SAN. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/


<!-- ===== Page 102 ===== -->

90

7 Cardiovascular System I: The Heart

Fig. 7.5. Conduction system in the heart. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/
branches before dividing into the multiple ﬁbres of the Purkinje system. This distributes the impulse over the inner walls of the ventricles causing contraction.
Although the SAN alone would produce a constant rhythmic heart rate, there are regulating factors present, as the heart rate may need to increase, for example during increased physical activity, or to decrease, for example when sleeping. This is largely controlled by the AVN and we will look at this in more detail later. Most of the changes in heart rate are mediated through the cardiac centre in the brain via the sympathetic and parasympathetic nervous systems, which will be examined in Chap. 10. Obviously, there are a large number of factors involved in setting the heart rate, such as body temperature, ion concentrations, oxygenation levels, blood pressure and even emotions (although how emotions, such as stress, drive your heart rate is a very complicated subject).
Heart rate increases to raise Cardiac Output (CO) since stroke volume is largely constant (Eq. 7.3). There are only three factors that can affect CO: the ﬁlling pressure of the right heart (the preload), the resistance to outﬂow from the left ventricle (the afterload) and the functional state of the heart. The last includes heart rate and contractility: the ability of cardiac muscle to generate force for any given ﬁbre length. The stroke volume is known to vary with the ventricular end-diastole volume (EDV), according to the Frank-Starling law of the heart, such that an increase in this volume causes an increase in stroke volume.
Figure 7.6 shows the pressure and volume changes during the cardiac cycle, ﬁrstly over time (LHS) and then against each other (RHS), for the left ventricle. The second of these plots is used for any cycle, rather like an internal combustion


<!-- ===== Page 103 ===== -->

7.4 Electrical Activity of the Heart

91

Fig. 7.6. Cardiac pressure volume cycle (LV = Left ventricle). This ﬁgure is taken, without changes, from Wikimedia under license: https://creativecommons.org/licenses/by-sa/2.5/deed.en
engine, where the area enclosed by the loop is the work done to power the cycle (in the human body this must come from metabolism). Increases in preload raise stroke volume, but increases in afterload decrease stroke volume, as the loop moves upwards and the left side to the right. Increases in contractility move the end systolic pressure-volume relationship (ESPVR) line upwards, thus increasing stroke volume since line D moves to the left.
7.4.4 Introduction to Electrocardiography
The pumping cycle is controlled by a conduction system to give a series of events in a very well-deﬁned order. The conduction system generates current densities through the membrane activity of the heart muscle cells and this is important in how we measure electrical activity in the heart. The ionic currents ﬂow in the thorax, which contains no other sources or sinks and is thus an almost entirely passive medium.
Currents ﬂowing through resistive loads produce voltages: they are of course very small, but, by placing electrodes at different positions on the human body, potential differences can be recorded. These potential differences form the basis of the ElectroCardioGram (ECG). There are of course difﬁculties involved in attempting to measure very small potential differences (of the order of a few mV) on a living human, but we won’t look at those here. We will conﬁne ourselves to understanding the production and interpretation of the signal.
The ECG is based on the idea of an equilateral triangle (known as Einthoven’s triangle) with the heart as a current source at the centre. Since the potential difference depends upon both the current magnitude and direction, the ECG is a vector quantity. The three bipolar leads, i.e. measurements made between two points, are known as Lead I (right arm to left arm), Lead II (right arm to left leg) and Lead III (left arm to left leg): hence the idea of a triangle, as shown in Fig. 7.7. There are then a further nine unipolar leads, i.e. measurements made at one point:


<!-- ===== Page 104 ===== -->

92
Fig. 7.7. Locations of leads used in ECG. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/ licenses/by/3.0/

7 Cardiovascular System I: The Heart

aVR (right arm), aVL (left arm), aVF (left leg) and V1–V6, as shown in Fig. 7.7, where V1–V6 run from left to right across the chest. Note that this naming system is simply the convention that is used for historical reasons.
Although each of these 12 leads will give a different output, the characteristics of the heart cycle are most clearly shown in lead II, since this pair aligns most closely with the major axis of potential differences in the heart. A typical waveform is shown in Fig. 7.8. It is labelled at various points: P, Q, R, S and T.
P wave: The depolarisation of the atria prior to atrial contraction causes a small low-voltage deﬂection, followed by a delay.
QRS complex: The depolarisation of the ventricles prior to ventricular contraction causes a large voltage deﬂection: this is the largest-amplitude section of the ECG. Although atrial repolarization occurs before ventricular depolarisation, the resulting signal is very small and thus not seen.
T wave: Ventricular repolarization. This last section is much the most variable and often very hard to see.
The sections between these features are close to zero potential, since there are few other sources of potential difference.


<!-- ===== Page 105 ===== -->

7.4 Electrical Activity of the Heart

93

Fig. 7.8. Schematic of ECG signal. This ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/
A great deal of research has been done to interpret the ECG in terms of providing clinical diagnoses. The simplest measure that can be extracted is the heart rate, normally taken as the inverse of the time between successive R peaks (the RR interval), measured in beats per minute. A trained clinician will also be able to infer a very large amount of information about the state of the heart from simply looking at an ECG, using changes in the relative timings and amplitudes of different sections of the ECG. Measurement of the ECG is also simple and cheap, meaning that it is normally the ﬁrst monitoring device attached to a patient. Note that Fig. 7.8 shows a perfectly regular heartbeat, which is not what is actually found: in fact the variability in your heart rate is a good sign and this can also tell us a lot about how the heart is working.
Exercise B
(a) What is the heart rate (in beats per minute) of the patient with the ECG shown in Fig. 7.8? Is there any variability from beat to beat?
(b) By holding the ﬁngers of one hand against the other wrist, estimate your heart rate in beats per minute. After a short period of light exercise, estimate it again. Comment on why the values are different.


<!-- ===== Page 106 ===== -->

94

7 Cardiovascular System I: The Heart

A brief summary of the cardiac cycle is shown in Fig. 7.9, relating the ECG to the pressure and volume changes. Check that you can follow the process from both a mechanical and an electrical point of view. There is ejection during systole, which is generated by ventricular depolarisation (shown by the QRS complex), which causes the pressure in the left ventricle to increase rapidly and the volume to drop. When the pressure rises above the aortic pressure, the aortic valve opens and blood leaves the ventricle: the pressure thus drops and when it drops below aortic pressure the aortic valve closes again. Ventricular repolarization occurs during the remainder of systole (shown by the T wave) whilst the ventricles slowly return to their steady state conditions.
Note that there are characteristic heart sounds, which are also shown in Fig. 7.9. The ﬁrst heart sound is low frequency and associated with closure of the atrioventricular valves; the second is higher frequency, reﬂecting a longer ejection period in the right ventricle; and the third is associated with rapid reﬁlling. There is a fourth sound, corresponding to atrial systole, but this is not normally audible.

Fig. 7.9. Cardiac cycle. This ﬁgure is taken, without changes, from Wikimedia under license: https://creativecommons.org/licenses/by-sa/2.5/deed.en


<!-- ===== Page 107 ===== -->

7.5 Conclusions

95

7.5 Conclusions

In this chapter we have looked at the human heart: how it is constructed, how it works as a pump and how this is controlled. We have also looked at how we measure how it is performing, both in terms of the cardiac output and the ECG. In the next chapter we will look at the rest of the cardiovascular system and its interaction with the heart.


<!-- ===== Page 108 ===== -->

Chapter 8
Cardiovascular System II: The Vasculature

In the previous chapter, we looked at the centre of the cardiovascular system, the heart. The heart is responsible for receiving blood and pumping it out again. This blood passes round the body through the vasculature, which is the complete set of blood vessels in every part of the human body. In this chapter, we will look at these blood vessels, how we can model them mathematically and how they contribute to the maintenance of homeostasis.
8.1 Anatomy of the Vascular System
Blood vessels divide into ﬁve main types: arteries, arterioles, capillaries, venules and veins. Blood passes through them in that order and they can be distinguished by differences in size, characteristics and function. Blood exiting the heart ﬁrst ﬂows through the aorta, which divides into arteries. These divide in turn into arterioles then capillaries before joining together in venules before entering the heart from the veins via the venae cavae. A schematic is shown in Fig. 8.1, where we will explain many of the details shown in later sections. The vessels shown in bright red are oxygenated, whereas the vessels shown in dark red are de-oxygenated, since the oxygen carried by the blood has been transferred to the surrounding tissues in the capillaries.
The arteries are thick-walled vessels that expand to accept and temporarily to store some of the blood ejected by the heart during systole and then to pass it downstream by passive recoil during diastole. As the arteries branch off, their diameter decreases, but in such a manner that the total cross-sectional area increases several-fold. The arteries have a relatively low and constant resistance to the ﬂow.
The artery walls comprise three layers: the tunica intima (or tunica interna), the tunica media and the tunica adventitia (or tunica externa), which are simply the inner, middle and outer layers. The middle layer is mainly smooth muscle and is

© Springer International Publishing Switzerland 2016

97

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_8


<!-- ===== Page 109 ===== -->

98

8 Cardiovascular System II: The Vasculature

Fig. 8.1 Schematic of different blood vessel types and structure (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
usually the thickest layer: it is important as it both supports the vessel and changes diameter to regulate the blood ﬂow and blood pressure. A schematic of the artery and vein wall structures is also shown in Fig. 8.1.
The arterioles have much thicker walls in proportion to their size than the arteries and have a much greater ﬂexibility to change their diameter and hence their resistance to ﬂow, due to them having lots of smooth muscle. The overall cross-sectional area is again much larger than the arteries but they have a high and changeable resistance, which allows for regulation of blood ﬂow.
The capillaries are the smallest vessels with very thin walls that contain no smooth muscle: their resistance is thus largely unchanging. The cross-sectional area is now at its largest: the ﬂow velocity is very small and this is where most of the exchange processes occur. The density and distribution of the capillaries depends upon the requirements of the local body tissues: where tissue consumes lots of oxygen, there will be a greater density than where tissue consumes less. This consumption level is termed the metabolic rate: tissues such as skeletal muscle, liver and kidney have a high rate and thus very many capillaries.
A reverse branching process occurs as the ﬂow enters the venules and the veins: the vessels branch back together again and the ﬂow velocity increases as the cross-sectional area decreases. The venous vessels have very thin walls in proportion to their diameters: as a result they are very compliant and increase in volume signiﬁcantly as the pressure changes (unlike the arterial and capillary vessels).


<!-- ===== Page 110 ===== -->

8.1 Anatomy of the Vascular System

99

Table 8.1 Structural properties of the vascular system Aorta Arteries Arterioles Capillaries

Internal diameter Wall thickness Length Number

25 mm 4 mm 2 mm 1 mm

40 μm 20 μm

7 μm 1 μm

0.4 m 1

20 mm 280

2 mm 20 × 106

0.5 mm 16 × 109

Venules 40 μm 7 μm
0.5 mm 160 × 106

Veins 7 mm 0.5 mm 25 mm 260

Venae cavae 30 mm
1.5 mm
0.3 m 1

They normally contain approximately 70 % of the total blood volume at any one time. Just as the arterioles are used to control the resistance, so the venous vessels are used to control the blood volume.
There are valves in medium and large veins to prevent blood from ﬂowing backwards, since the veins are mostly travelling up towards the heart and there is very little pressure to force the blood forwards. Venous return primarily depends upon skeletal muscle action, respiratory movements and the constriction of smooth muscle in the venous walls.
Table 8.1 summarises the structural properties of the different parts of the vascular system in more detail: we will consider how these affect the behaviour of the cardiovascular system once we have considered the mechanics of blood ﬂow through vessels in more detail. Note that the number of branches is very large, as the cardiovascular network must cover the entire body.

8.2 Blood
Blood consists of two elements: plasma and blood cells. Approximately 40–45 % of the volume of blood is occupied by blood cells that are suspended in a watery ﬂuid called plasma. The fraction of blood volume occupied by cells is called the haematocrit. The plasma consists of ions in solution and many plasma proteins. By weight it comprises about 90 % water and 7 % plasma protein, with the remainder made up of other organic and inorganic substances. Blood cells are divided into erythrocytes (red blood cells), leucocytes (white blood cells) and platelets, as shown in Fig. 8.2. Although they are all produced in the red bone marrow, they have different functions and white blood cells come in a large number of types.
The red blood cells are by far the most numerous and they contain the haemoglobin that is responsible for the transport of oxygen. They are biconcave discs and deform easily to pass through the capillaries, since they are approximately 7 μm in diameter. White blood cells defend the body against infection whilst platelets play an important role in haemostasis (the formation of blood clots in response to damage to the vessel wall). An adult human contains approximately 5.5 L of blood.


<!-- ===== Page 111 ===== -->

100

8 Cardiovascular System II: The Vasculature

Fig. 8.2 Red blood cell, platelet and white blood cell, isolated from a scanning electron micrograph (this ﬁgure is taken, without changes, from OpenStax College under license: http:// creativecommons.org/licenses/by/3.0/)

8.3 Haemodynamics

Haemodynamics is the study of the ﬂow of blood. Since blood is a ﬂuid, it can be treated like any other ﬂuid. We will start here by assuming that the ﬂuid is Newtonian, that the ﬂow is laminar and steady and that the vessel in which it is ﬂowing is straight and rigid. Although this might seem to be a lot of assumptions to
make, it actually gives us a very important result.
In the exercise below, you can derive the following relationship between the pressure difference along a blood vessel and the ﬂow rate through it:

Dpq ¼ pR4 8lL

ð8:1Þ

where the viscosity of blood is µ and the vessel has radius R and length L. This is in fact a fairly standard result for any ﬂuid and turns out to be surprisingly useful in
haemodynamics. It introduces us to the concept of hydraulic resistance, which
says that when a pressure difference is applied between two ends of a blood vessel, a ﬂow through the vessel will result that is linearly proportional to this pressure difference. The ratio between applied pressure difference and resulting ﬂow is then
termed hydraulic resistance. This is given by the RHS of Eq. 8.1 and is only dependent upon the vessel geometry and the viscosity of the ﬂuid. Blood ﬂowing in
large vessels has a viscosity approximately three times that of water.


<!-- ===== Page 112 ===== -->

8.3 Haemodynamics

101

Exercise A The equation governing ﬂow in a cylinder is:

@ðrsÞ ¼ r dp

@r

dx

ðA:1Þ

where r is radial position, p the ﬂuid pressure (which is only a function of axial distance, x) and shear stress for a Newtonian ﬂuid is given by:

s ¼ l @u @r

ðA:2Þ

Given that the ﬂuid velocity must be zero at the wall, where r = R, and that
there must be zero gradient at the origin, show that the velocity proﬁle of the ﬂuid can be given by:

u ¼ 1 Àr2 À R2Á dp

4l

dx

Hence calculate the ﬂow rate and show the result given in Eq. 8.1.

ðA:3Þ

This idea of resistance to ﬂow, which is simply a measure of the friction caused by viscosity in the ﬂow, is very similar to electrical resistance. In a resistor, when a potential difference is applied between the two ends, current ﬂows, linearly pro-
portional to this potential difference.
We can thus use this idea to develop something called an equivalent electrical circuit. In the same way that we can write the equation for a resistor (i.e. Ohm’s
law):

DV ¼ R I

ð8:2Þ

we can also write:

Dp ¼ R q

ð8:3Þ

where the equation describing electrical current ﬂow is mathematically identical to that describing blood ﬂow in a blood vessel.
We can thus draw an electrical equivalent circuit for any number of blood
vessels in exactly the same way that we draw an electrical circuit for any number of
resistors. In this analogy, voltage (strictly potential difference) equates to pressure difference, current relates to blood ﬂow and the ratio of the two is resistance
(electrical resistance or hydraulic resistance). The fact that there is such a close


<!-- ===== Page 113 ===== -->

102

8 Cardiovascular System II: The Vasculature

correspondence between the two is why the analogy is used so frequently in this
and other contexts.
Hydraulic resistances can be put in series and in parallel in exactly the same way
as electrical resistances (see Exercise B). The arteries, arterioles, capillaries, venules and veins ﬂowing in each body organ are in series, since blood ﬂows through them
consecutively, whereas the body organs are predominantly in parallel, since blood ﬂows through them simultaneously.

Exercise B
Show that a network of N blood vessels, each of resistance R, has an overall resistance R=N when placed in parallel.

Exercise D asks you to calculate the resistances of all of the different parts of the vascular network. You will ﬁnd that the resistance is dominated by the arterioles:
this is why they are predominantly used to adjust the overall vascular resistance. As their resistance drops, ﬂow rate increases for ﬁxed blood pressure or blood pressure drops for ﬁxed blood ﬂow. They do, of course, only adjust the resistance within
certain limits, since blood vessels can only change resistance through changes in diameter. The blood ﬂow through each body organ can also be altered by adjusting the relevant arteriolar resistance: since the organs are in parallel, the blood ﬂow can be changed for one organ without having a signiﬁcant effect on the remainder of the
vascular system (and of course an increase can also be provided by an increase in
cardiac output).
We have made a large number of assumptions to derive Eq. 8.1, none of which are strictly true. The most important are that the ﬂow is not steady (remember that
the heart is a pulsatile pump) and that the vessel radius is not constant. The effects
of pulsatility and an expanding wall diameter are often modelled by means of two
extra electrical components. Inductance is used to model the inertia of the ﬂuid whereas capacitance is used
to model the storage of blood in vessels, due to the elasticity of the vessel walls: normally called compliance. This storage is a very important feature of the vascular
system: in fact, the arteries and veins behave more like balloons with a single
pressure, rather than resistive pipes with a continuous decrease in pressure. The inductance of a blood vessel is found from solving the Navier–Stokes
equations (the equations that govern the behaviour of all ﬂuids) under certain
conditions. For simplicity, we will just quote the result here, although it can be
derived from the equations in Chap. 6:

I ¼ pR2 qL

ð8:4Þ

where ρ is the density of blood. Note that we will use I for inductance, rather than L, for obvious reasons.


<!-- ===== Page 114 ===== -->

8.3 Haemodynamics

103

The compliance of a blood vessel is very simply deﬁned as the rate of change of volume with pressure:

C ¼ dV dp

ð8:5Þ

where we normally deﬁne the pressure here as the difference between internal and external pressure (rather than the difference between inlet and outlet pressure). Compliance is analogous to capacitance, which is deﬁned as the rate of change of charge with potential difference.
The compliance depends upon the geometry and properties of the vessel wall. Exercise C asks you to derive the following expression for compliance:

C ¼ 3pR3L 2Eh

ð8:6Þ

This assumes that the vessel wall is of thickness h and made up of a linear elastic material with Young’s modulus E and Poisson’s ratio of 1/2. This value of Poisson’s ratio relates to an incompressible material, which is in fact a good approximation for the tissue that makes up a vessel wall, as we discussed in Chap. 6.

Exercise C
(a) Show that the compliance of a vessel is given by Eq. (8.6). Assume that the material is linear and elastic with Young’s modulus E and Poisson’s ratio of 1/2. The incremental stress components can be taken to be those for a thin-walled vessel:

drh ¼ dp R h

ðC:1Þ

drz ¼ dp R 2h

ðC:2Þ

drr ¼ 0

ðC:3Þ

(b) Show that a network of N capacitors, each of capacitance C, when

placed in parallel has total capacitance CN.

We can combine all three of these electrical elements to derive the equivalent circuit shown in Fig. 8.3 for any type of vessel. Note that we have placed the capacitor in this equivalent electrical circuit at the outlet, but other models will place it in the middle or at the inlet: there is no unique way of doing this. We can use the values given in Table 8.1 to calculate values of resistance, inductance and compliance for every type of blood vessel, as in the exercise below.


<!-- ===== Page 115 ===== -->

104

8 Cardiovascular System II: The Vasculature

Fig. 8.3 Equivalent electrical circuit for blood ﬂow
Exercise D
Calculate the values of resistance, inductance and compliance for all the different types of vessel listed in Table 8.1. Assume that vessels have a Young’s modulus of 3 kPa and that blood has a density of 1050 kg/m3.
Although we have only considered a single vessel, larger networks of vessels can be built by adding the equivalent circuits in series and parallel as necessary. It is common to simplify the larger networks by neglecting some resistances and capacitances and merging others.
One simple realistic equivalent circuit model of a body organ comprises seven components, as shown in Fig. 8.4. Obviously this requires some knowledge of the physiology and a number of assumptions. Note that we nearly always neglect capillary inductance and compliance, as done here, since these tend to be very small compared to the other components. The simplest model of the systemic circulation then becomes a series of organs in parallel, where each body organ is supplied by the aorta and drains into the venae cavae.
The compliance of the arteries is vital in converting the pulsatile nature of the ﬂow exiting the heart into a continuous ﬂow. During systole, the ﬂow of blood into the arteries is greater than that exiting into the arterioles, so the arteries expand, contracting during diastole. There is a storing of energy during the ﬁrst stage, which is then used to propel the blood forward during the second stage. By the time that the ﬂow has reached the capillaries, it is virtually steady state, as you will show in the exercise below.

Fig. 8.4 Approximate equivalent electrical circuit for body organ


<!-- ===== Page 116 ===== -->

8.3 Haemodynamics

105

Exercise E
(a) Derive an expression for the ﬂow through the capillaries in terms of the pressure difference between inlet and outlet for the circuit shown in Fig. 8.4. Use phasor notation where the impedance of an inductor is Z ¼ ixI and the impedance of a capacitor is Z ¼ 1=ixC. Assume for simplicity that venous (outlet) pressure is negligible.
(b) Explain how this circuit acts like a low-pass ﬁlter. Why is this important?

We can derive more complex equivalent circuits using more detailed models of the ﬂuid ﬂow and the vessel wall. In particular, the vessel wall is not a passive
elastic material and the relationship between pressure and volume is more like an
exponential rise than a straight line (so blood vessels get less compliant as they get bigger, as you would expect from Fung’s model in Chap. 6). Although this can be
modelled using a capacitance that varies with pressure, the model then becomes
non-linear and considerably harder to analyse.

8.4 Blood Pressure
The body’s pulse can easily be felt at the wrist by pressing your ﬁngers against the inside of your wrist. This is simply caused by the regular beating of the heart forcing an artery to expand and contract rhythmically as pulses of blood pass through the artery. When we talk about blood pressure, we conventionally mean Arterial Blood Pressure (ABP), which is the pressure found in the arteries and their branches. This pressure varies between a high pressure, caused by ventricular contraction, which is termed systolic, as it occurs during systole, and a corresponding low pressure, termed diastolic, as it occurs during diastole. An example waveform is shown in Fig. 8.5: note that the rise is much sharper than the subsequent fall. Also visible is the ‘dicrotic notch’, which is the sudden drop and rise in ABP that occurs when the aortic valve closes (see the previous chapter for details). Since there is a peak in blood pressure every time the heart beats, heart rate can be calculated from the blood pressure, in a similar manner to methods used for the ECG.
ABP is nearly always measured in units of millimetres of mercury (mmHg), rather than in Pascals, since the resulting numbers are around 100, which makes them easier to quote (the conversion factor is 1 mmHg = 133 Pa). Normally, only the systolic and diastolic values of blood pressure are measured for each heart beat and this is then recorded in the form systolic over diastolic (for example a systolic


<!-- ===== Page 117 ===== -->

106

8 Cardiovascular System II: The Vasculature

Fig. 8.5 Arterial blood pressure waveform (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)

blood pressure of 120 mmHg and a diastolic blood pressure of 80 mmHg would be quoted as 120/80).
Mean arterial blood pressure (MAP) is also of interest, since it gives the average effective pressure that drives blood through the systemic circulation. Although it should strictly be calculated by integrating the blood pressure waveform over time, often only the systemic and diastolic values are known. The most common weighted combination of the two is:

MAP ¼ DBP þ SBP À DBP 3

ð8:7Þ

where SBP and DBP represent systolic and diastolic blood pressures respectively.
Although it would seem more logical simply to average the SBP and DBP, it turns
out that for a typical waveform, this weighting is more representative of the
time-averaged value. There are some other relationships that we use to help to understand the ﬂow of
blood through the body. We have already come across Cardiac Output and the concept of resistance to ﬂow, so we introduce the idea of Total Peripheral
Resistance:

TPR ¼ MAP CO

ð8:8Þ

which is essentially Eq. 8.3 applied to the whole body. Of course in this equation we are assuming that the blood pressure at return to the heart is zero. Although very simple, Eq. 8.8 does tell us that to change MAP the body must either change CO or TPR. We will look at both of these later.
We also deﬁne the Arterial Pulse Pressure (APP) to be:

APP ¼ SBP À DBP

ð8:9Þ


<!-- ===== Page 118 ===== -->

8.4 Blood Pressure

107

i.e. the difference between the maximum and minimum value of arterial pressure during each heartbeat. It turns out that there is an approximate relationship between APP and heart stroke volume:

APP ¼ SV Ca

ð8:10Þ

where Ca is arterial compliance.
Changes in APP are thus caused either by a change in heart stroke volume or arterial compliance. It can be seen that MAP and APP are in many ways more useful measures of how the cardiovascular system is behaving than SBP and DBP.
Blood ﬂow through the body has one predominant frequency, which is the heart rate (although there are actually many other frequency components to a blood pressure signal, caused by respiration and other processes within the human body). The equivalent circuit shown in Fig. 8.4 has several sections that can be thought of as ﬁlters, whereby frequency components are removed.
A resistor and inductor in series have a time constant:

I qL pR4 qR2 s¼ ¼ 2Á ¼
R pR 8lL 8l

ð8:11Þ

If we assume that the dominant frequency is 1 Hz (the heart beat), then for the inductor to be important, we need:

x [ 1s

ð8:12Þ

i.e. the frequency of oscillation must be greater than the cut-off frequency. This will be true when:

sﬃﬃﬃﬃﬃ R [ 4l
pq

ð8:13Þ

Since blood has roughly the same density as water and three times the viscosity, this turns out to be approximately 2 mm. Inductance is thus only important in vessels above this size (which is why we only included it in Fig. 8.4 for the arterial and venous compartments).
A resistor and capacitor have time constant:

s ¼ RC ¼ 12lL2 ERh

ð8:14Þ

This will be important in long vessels with thin walls and low values of Young’s modulus. This makes it most important for the venous compartment. In fact arterial


<!-- ===== Page 119 ===== -->

108

8 Cardiovascular System II: The Vasculature

compliance also turns out to be very useful in the control of blood ﬂow (as we will see in Sect. 8.5), so this is normally retained.

Exercise F
For the circuit shown in Fig. 8.4, derive a simpliﬁed expression for the transfer function of the circuit, neglecting inductance. What is the time constant and what condition must be satisﬁed if this circuit is to remove oscillations in capillary ﬂow due to pulsatile ABP?

8.4.1 Long-Term Measurement Techniques
Measurements of blood pressure are very important to doctors when assessing the risks of a whole range of vascular diseases, for example strokes, where the risk of a stroke goes up rapidly with increased blood pressure. Elevated blood pressure (hypertension) will normally be treated through the use of anti-hypertensive drugs that act to lower MAP.
Blood pressure is normally measured using a sphygmomanometer, which consists of an inﬂatable cuff that is placed around the upper arm over the brachial artery and connected to a pressure gauge. The pressure gauge is usually a column of mercury. The cuff is inﬂated to a pressure well above the systolic pressure (in the region 175–200 mmHg): since this is higher than the largest arterial pressure, the blood vessels collapse, preventing blood ﬂow to or from the forearm. A stethoscope is then placed over the artery just below the cuff and the cuff pressure allowed to fall gradually: as soon as the cuff pressure falls below the peak arterial pressure, some blood passes through the arteries, but only intermittently. This gives the value of SBP.
Since this ﬂow is turbulent and intermittent, tapping sounds, known as Korotkoff sounds, are produced. As the pressure continues to drop, the sounds increase in volume before decreasing again. The pressure at which the sounds disappear completely is the DBP. Since these sounds are often difﬁcult to hear near the diastolic pressure, accurate determination of the DBP is often a matter of experience. This technique is known as the auscultatory technique, since it is based on listening to sounds, and is illustrated in Fig. 8.6.
It is also possible to use oscillometry to measure blood pressure. This is performed using a cuff with an in-line pressure sensor. Again, the cuff is pressurised above SBP and allowed to deﬂate: the measured cuff pressure is high-pass-ﬁltered above 1 Hz to observe the pulsatile oscillations as the cuff deﬂates. The point of maximum oscillation corresponds to a cuff pressure equivalent to MAP. Both SBP and DBP are found where the amplitude of the oscillations is a ﬁxed percentage of the maximum amplitude: 55 % for SBP and 85 % for DBP.


<!-- ===== Page 120 ===== -->

8.4 Blood Pressure

109

Fig. 8.6 Blood pressure measurement (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
8.4.2 Short-Term Measurement Techniques
We should note that both of these methods have a measurement time that is much longer than any individual heart beat period: they are thus used for occasional samples rather than as continuous measures. Some attempts have been made to provide a continuous measure of blood pressure. The continuous vascular unloading technique works on the basis of continuously adjusting the cuff pressure to the arterial pressure: this is done using mechanical feedback. The main disadvantage of this technique is that it can only be applied at a peripheral vascular location such as the ﬁnger, where it may not be an accurate representation of true arterial blood pressure. There are a variety of other possible techniques, each with advantages and disadvantages, which we will not consider here.
8.5 Measurement of Blood Supply
As well as measuring blood pressure, we are often interested in measuring blood ﬂow to different parts of the body. Blood carries nutrients to body organs and so blood supply must be provided continuously, particularly to organs such as the brain and heart. Cardiac output is adjusted to provide sufﬁcient total blood ﬂow and the resistances of different body organs are also altered to ensure that each organ receives enough ﬂow.


<!-- ===== Page 121 ===== -->

110

8 Cardiovascular System II: The Vasculature

An important function of the circulation is to support metabolism by supplying nutrients and removing waste. Thus we are often interested at the capillary level less in blood ﬂow and more in terms of blood supply or perfusion. Perfusion measures the rate of delivery of blood to a volume of tissue, rather than simply the ﬂow rate through the vessels; thus it has units of volume of blood per volume of tissue per unit time, typically ml blood/ml tissue min−1. As we will see in Chap. 9, the delivery and the removal of gases are essentially perfusion limited processes, because these predominantly happen over the large surface area of the capillary bed, i.e. it is perfusion that determines how much is delivered to and taken away from tissue.

8.5.1 Blood Flow
The easiest and simplest way to measure blood ﬂow is through measurements of blood ﬂow velocity. This can be done using a Doppler probe, whereby an ultrasound signal with frequency of order 2 MHz is sent out towards a blood vessel. The movement of the blood in the vessel causes a phase shift, which can be measured in the returning signal.
The most common use of Doppler is in the brain, where it is called transcranial Doppler (TCD). This has been widely used since the 1980s to monitor cerebral blood ﬂow, although recordings have to be made in what are known as insonation windows, since ultrasound signals are blocked by bone.
It is important to remember that Doppler ultrasound only measures blood ﬂow velocity and so calculating blood ﬂow requires an assumption about the cross-sectional area of the vessel to be made. This area can vary under certain conditions, but measuring this area is very difﬁcult and can only really be done using high-resolution imaging.

8.5.2 Perfusion
Perfusion is a key measure of how many organs behave. Hypoperfusion (a drop in perfusion) can have a very detrimental impact on organs such as the heart and brain. In the brain, hypoperfusion can be the result of either a blockage in a supply vessel or a bleed in a major blood vessel in the brain: these cause an ischaemic stroke or a haemorrhagic stroke respectively. In the heart, hypoperfusion in the blood vessels supplying heart muscle can cause a heart attack, as described in the previous chapter.
Since perfusion is so important to body organs, there has been a lot of interest in measuring perfusion, mainly using imaging techniques to generate perfusion maps. The common factor to all of these is the use of a contrast agent that acts as a tracer: the basic principle is that ﬂow is measured by tracking a substance that moves and


<!-- ===== Page 122 ===== -->

8.5 Measurement of Blood Supply

111

the concentration of which can be followed. Two very common examples are Positron Emission Tomography (PET) and Magnetic Resonance Imaging (MRI).
In PET, a radioactive tracer is injected into the bloodstream: this is most commonly a sugar called F-18 labelled ﬂurodeoxyglucose (FDG). This gradually accumulates in the organ of interest before it disperses away and the radioactivity decays below a detectable level: a time series of the concentration can then be used to estimate perfusion (see Chap. 5). In MRI, the most common tracers are based on gadolinium, which is a material whose magnetic properties mean that its presence in tissue alters the MRI image in direct proportion to its concentration.
MRI can also use the water in blood as a naturally occurring, or endogenous tracer. This is most often done in the brain, when the magnetism of blood water is inverted in the neck before imaging in the brain. This process, known as Arterial Spin Labelling (ASL) allows water accumulation in tissue to be seen, by which time it has had time to exchange from the blood into the tissue, so that perfusion can be measured. This technique avoids the need for injections, but does then give a poorer signal to noise ratio.

8.6 Control of Blood Flow
The fact that body organs need a continuous supply of blood means that the body has a variety of mechanisms to maintain this blood supply. We will look at the ways in which the central control mechanisms control blood ﬂow to an organ in the ﬁnal chapter: we consider here how individual vessels locally control perfusion. This happens primarily within an organ at the arteriolar level (remember that these are the vessels with the most smooth muscle and the greatest contribution to resistance), although there is thought to be some control at the capillary level too.

8.6.1 Individual Vessels
In Exercise G you will show that, for ﬁxed compliance, ﬂow is proportional to vessel radius to the power 6 and that shear stress is proportional to vessel radius to the power 3. These mean that the vessel is extremely sensitive to even quite small changes in vessel radius. In fact, the vessel wall is thought to respond to a large number of stimuli, including shear stress, and these combine to give a signal that acts to control blood ﬂow. Precisely how this works is not well understood, although it is known that nitric oxide and intracellular calcium play important roles in the behaviour.


<!-- ===== Page 123 ===== -->

112

8 Cardiovascular System II: The Vasculature

Exercise G
Consider a vessel of ﬁxed length with driving pressure P at the inlet and zero pressure both at the outlet and outside the vessel.
(a) If the vessel compliance is constant, show that ﬂow through the vessel is proportional to vessel radius to the power 6.
(b) Show also that shear stress is proportional to vessel radius to the power 3.

In fact, vessel compliance changes as the vessel alters in size. In Exercise H you will show that for an incompressible vessel, the vessel wall gets thinner as the vessel expands. Thus as pressure increases and the vessel wall gets thinner, compliance increases passively very rapidly (the numerator gets larger and the denominator gets smaller).
Exercise H
(a) Consider a vessel ﬁxed at both ends, initially with inner radius Ro and wall thickness ho. Assuming that the volume of the vessel wall does not change when the pressure increases, derive a relationship for the wall thickness as a function of the inner radius and the initial inner radius and wall thickness.
(b) Using the expression for resistance (Eq. 8.1), explain how resistance changes as pressure (and hence inner radius) increases.
(c) Does the vessel wall become stiffer or more compliant as pressure increases?

However, in reality vessels become less compliant with increased diameter due to the active mechanisms involved in autoregulation of blood ﬂow. The ﬁnal
response of a blood vessel to a decrease in blood pressure is thus made up of two
components: the early passive response that leads to an increase in diameter and a decrease in blood ﬂow; and the subsequent active response that counterbalances this response to maintain blood ﬂow nearly constant.

8.6.2 Individual Body Organs
One of the most tightly regulated body organs is the brain, where perfusion (known here as cerebral blood ﬂow) is kept nearly constant within a range of ABP of


<!-- ===== Page 124 ===== -->

8.6 Control of Blood Flow

113

approximately 50–150 mmHg. It does this by tightly controlling blood ﬂow through the arterioles, where there are a lot of smooth muscle cells. Precisely how this is done is still not entirely fully understood, but impaired autoregulation in the brain is found in a wide range of brain diseases, such as stroke, dementia and brain injury.
Body organs, of course, do not just regulate their blood supply in response to pressure, but must also match blood (and hence nutrient) supply to metabolic demands. If the cells need greater oxygen, more blood must be supplied. In the brain this will only be a relatively small change, but in some organs, such as skeletal muscle, the increase in blood supply can be very large. The balance between these two can be modelled very simply.
Let’s consider a body organ with driving pressure difference P and metabolic rate of oxygen M. The equations governing ﬂow and metabolism can be written as follows:

ðCa À CvÞQ ¼ M P ¼ RQ

ð8:15Þ ð8:16Þ

where Ca and Cv are arterial and venous oxygen concentrations. The ﬁrst equation comes from conservation of mass (remember cardiac output in the previous chapter) and the second one is simply Eq. 8.3.
We will assume to start with that resistance responds to changes in venous oxygen concentration linearly, so that a decrease in venous oxygen concentration results in a decrease in resistance:

R ¼ Roð1 þ ACvÞ

ð8:17Þ

where A is a constant (rather like the gain in a feedback circuit). The ﬂow through the organ is then given by:





Q ¼ 1 MA þ P

1 þ ACa

Ro

ð8:18Þ

Obviously if A = 0, there is no regulation and ﬂow is linearly proportional to pressure. However, as A increases, there is greater feedback and ﬂow becomes less
sensitive to pressure.
If we reference everything back to baseline conditions (denoted by the overbar), then we can re-write the equation for ﬂow as:

Q ¼ a M þ ð1 À aÞ P

QM

P

ð8:19Þ

where:


<!-- ===== Page 125 ===== -->

114

8 Cardiovascular System II: The Vasculature

a ¼ AMRo P þ AMRo

ð8:20Þ

This means that ﬂow responds to both changes in metabolism (with sensitivity a) and to blood pressure (with sensitivity 1 À a). There is a trade-off between these two, with it being desirable to have higher sensitivity to changes in metabolism than
to changes in pressure. This is achieved by having:

A) P MRo

ð8:21Þ

i.e. a high level of feedback. However, any system with too much feedback can become unstable, so it is not as simple as aiming for as high a value as possible. This again is a trade-off between competing requirements.

8.6.3 Whole Body

Now that we have looked at the whole cardiovascular system, we will ﬁnish by considering the whole body and how the heart plays its part in controlling blood pressure. We divide the body into arterial and venous compartments, each of which has resistance and compliance. Assuming that both compliances are constant, we can state that total blood volume comprises arterial and venous compartments:

VT ¼ PaCa þ PvCv

ð8:22Þ

In the steady state we can also say that total resistance is related to pressure and ﬂow by:

Pa À Pv ¼ QRT

ð8:23Þ

This time, in order to maintain arterial blood pressure, we assume that cardiac output, Q, is proportional to heart rate, H, and venous pressure:

Q ¼ kHPv

ð8:24Þ

This is a simple approximation, based on the ability of the heart to provide greater cardiac output based on heart rate and preload.
From these, we can derive an expression for arterial pressure:

Pa ¼ VT ð1 þ kHRT Þ Cv þ Cað1 þ kHRT Þ

ð8:25Þ


<!-- ===== Page 126 ===== -->

8.6 Control of Blood Flow

115

At low values of heart rate, this approximates to:

Pa ¼ VT Cv þ Ca

ð8:26Þ

but at high values of heart rate, this approximates to:

Pa ¼ VT Ca

ð8:27Þ

which is larger. However, this is the maximum arterial blood pressure than can be achieved in this model and so continuing to increase heart rate to raise arterial blood pressure becomes less effective. The model also explains why as blood vessels become stiffer with age (and compliance decreases) baseline arterial blood pressure tends to increase.
We can plot this result, which is most easily done by converting it to non-dimensional form:

Pa  ¼ 1 þ 1   ð1 þ hðpr À 1ÞÞ  Pa prcr 1 þ hðpr À 1Þ þ 1cr

ð8:28Þ

where arterial blood pressure, as a fraction of its baseline value, is only a function of heart rate (now as a fraction of its baseline value), h, and the ratio of arterial to venous blood pressure, pr, and the ratio of arterial to venous compliance, cr. By writing the result with as few variables as possible in non-dimensional form, we can see that there are only two extra parameters determining the relationship between heart rate and blood pressure, making it much easier to interpret. The resulting relationship between heart rate and blood pressure is then shown in Fig. 8.7, where

Fig. 8.7 Relationship between heart rate and blood pressure in simple model


<!-- ===== Page 127 ===== -->

116

8 Cardiovascular System II: The Vasculature

we have taken pr = 10 and cr = 1/3 as typical values. The saturation is very clearly seen, where increases in heart rate have progressively less impact on arterial blood pressure.
In these two examples, we can see both how whole organ control is achieved through very simple feedback on oxygen concentration and whole body control through blood pressure and heart rate. Obviously the models that we are using are very simplistic, but they do illustrate the kind of behaviour that is seen in the human body and help to provide an insight into the underlying relationships.

8.7 Conclusions
In this chapter, we have examined the second part of the cardiovascular system: all the vessels that make up the vasculature. These can be modelled using very simple techniques and we have developed the equivalent electrical circuit model that is in very widespread use. We have examined how these models can be constructed and developed. We then investigated how blood ﬂow and perfusion can be measured and ﬁnished by considering how the body regulates blood ﬂow at a local level in addition to the global control that we looked at in the previous chapter.


<!-- ===== Page 128 ===== -->

Chapter 9
The Respiratory System

The respiratory system can roughly be divided into the upper airways in the head and neck, and the lower airways including trachea and all the structures in the lungs. The primary functions of the respiratory system are:
• Gas exchange—most importantly the movement of O2 into the body and CO2 out.
• Host defence—it provides one of the barriers between the outside world and the body inside.
• Synthesis and metabolism of various compounds.
9.1 The Lungs and Pulmonary Circulation
The lungs are contained in space with a volume of approximately 4 L but present a surface area of approximately 85 m2 for gas exchange. This is achieved thorough a highly branched structure, Table 9.1, the trachea branching into the two main stem bronchi which themselves divide into further bronchi at progressively small diameters. Subsequently further generations of the branches are called bronchioles before ﬁnally terminating in the alveoli. Both the smallest bronchioles and alveoli are involved in respiration over a gas-blood barrier that is only 1–2 μm thick. The pulmonary capillary bed is the largest in the body having a surface area of approximately 70–80 m2. The capillary volume of the lungs is 70 ml at rest, but can increase up to 200 ml during exercise. This is achieved through the recruitment of closed vessels or compressed capillary segments from an increase in pulmonary pressure when cardiac output is increased, along with an enlargement of the capillaries with a rise in internal pressure when the lungs ﬁll with blood.

© Springer International Publishing Switzerland 2016

117

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_9


<!-- ===== Page 129 ===== -->

118

9 The Respiratory System

Table 9.1. Branching structure of the lungs

Generation

Diameter (cm)

Length (cm)

Number

Total
cross-sectional area (cm2)

Conducting Trachea

0 1.80

12.0

1

2.54

zone

1 1.22

4.8

2

2.33

2 0.83

1.9

4

2.13

3 0.56

0.8

8

2.00

Bronchioles 4 0.45

1.3

16

2.48

Transitional and respiratory zones

Terminal bronchioles Respiratory bronchioles
Alveolar ducts

5 0.35 ⋮⋮ 16 0.06
17 ⋮ 18 19 0.05 20 ⋮ 21

1.07

32

3.11

⋮

⋮

⋮

0.17

5 × 104 180.0

⋮

⋮

⋮

0.10

5 × 105 103

⋮

⋮

⋮

Alveolar sacs

22 23 0.04

0.05

8 × 105 104

Following Weibel ER. Morphometry of the Human Lung. Springer Verlag and Academic Press, Heidelberg–New York 1963

9.1.1 Breathing
Figure 9.1 shows the breathing cycle. This is mainly achieved by the action of the diaphragm, although the external intercostal and scalene muscles in the chest also play a role. Air is drawn into the lungs by an increase in the chest cavity, pushing the abdominal content downwards. Exhalation is passive during normal breathing, but may involve active effort by muscles during exercise and hyperventilation.
The total lung capacity is the total volume of air that can be contained within the lung. Various other volumes and capacities can be deﬁned as shown in Fig. 9.2, where capacities are composed of two or more volumes. Under normal breathing only a relatively small range of the available lung volume is used.

9.1.2 Respiration Rate
The measurement of respiration rate at its simplest relies on counting the number of breaths per minute. This would typically require either a sensor at the mouth and/or nose to detect air movement of air in and out of the lungs, or a band around the chest. The latter is potentially able to measure changes in chest volume and thus to


<!-- ===== Page 130 ===== -->

9.1 The Lungs and Pulmonary Circulation

119

Fig. 9.1 The breathing cycle (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
Fig. 9.2 Deﬁnition of the various lung volumes (a) and capacities (b) (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
infer information about lung volume. Alternatively, it can be possible to extract information about respiration from EEG, since changes in the volume of the abdominal cavity will alter the conductivity and thus produce small ﬂuctuations in the ECG signal. These changes are typically very subtle and thus hard to observe in anything other than ideal conditions.


<!-- ===== Page 131 ===== -->

120
9.2 Gas Transport

9 The Respiratory System

Air is a mixture of various gases, predominantly nitrogen (78 %) with a large proportion of oxygen (21 %) and various other gasses (1 %) including carbon dioxide. We often refer to the partial pressures of each of the components, where the partial pressure of gas i is deﬁned by:

pi ¼ yip;

ð9:1Þ

where yi is the mole fraction of the gas and p is the total pressure of the gas mixture. Here the partial pressure is the pressure that this gas would exert if it alone were
present. Since in the lungs gases are (indirectly) in contact with a liquid, the blood,
we need to be able to relate partial pressure of a gas to its concentration in the blood. We can do this via Henry’s law:

ci ¼ ripi;

ð9:2Þ

where σ is the Ostwald solubility co-efﬁcient. Typical values for respiratory gases in plasma are given in Table 9.2. All of these solubilities are fairly similar and are in fact too small to carry sufﬁcient quantities of oxygen and carbon dioxide in the blood.

9.2.1 Inert Gases

A simple model for the transfer of gas across the capillary-alveoli interface assumes that the ﬂow is linearly proportional to the difference in partial pressures, thus:

À

Á

q ¼ Ds cb À rpg ;

ð9:3Þ

where q is the net ﬂux per unit area, pg is the partial pressure of gas in the air space, cb is the concentration of the gas dissolved in the capillary blood and Ds is the surface diffusion co-efﬁcient. Note that like a lot of the processes we have met in
this book, this is just a ﬁrst order equation with time.

Table 9.2 Solubility of respiratory gases in blood plasma

Substance O2 CO2 CO N2 He

σ (mM/mmHg) 1.4 × 10−3 3.3 × 10−2 1.2 × 10−3 7 × 10−4 4.8 × 10−4


<!-- ===== Page 132 ===== -->

9.2 Gas Transport

121

Exercise A
Starting with the diffusion equation in one dimension, show that the ﬂux of gas per unit area of membrane from the air space into the blood is given by Eq. 9.3, where it has been assumed that the gas has the same solubility in the membrane to that in the blood.

As you will see in Exercise A modelling the ﬂow of gas across the capillary-alveoli interface is very similar to Exercise 4A modelling passive transport through a cell membrane. Note that we haven’t worried about the relative solubilities of the gas in the membrane compared to the blood here. This is because the membrane we care about is the cellular layer that separates the gas space and the blood. These cells will have an aqueous interior and thus similar solubility to that of blood. We have ignored the diffusion through the cell membranes (and thus relative solubility of blood in the cell walls) because these are much thinner than the cells themselves.
A complete pulmonary capillary can be modelled as a cylinder with gas transport occurring over the full surface. In the limit the expression for total gas ﬂux reduces to:

Q ¼ f rðp0 À pinÞ;

ð9:4Þ

where pin is the partial pressure of the gas in the blood at the inlet to the capillary. Thus the gas ﬂux depends only upon the pressure difference and the blood ﬂow rate,
f. This only holds as long as the permeability of the membrane to the gas (i.e. the Ds value) is sufﬁciently high, which is primarily achieved in the lungs through having a thin membrane. Since the gas ﬂux depends on blood ﬂow and not the rate of
diffusion it is called perfusion limited.

Exercise B
Here we will derive the result in Eq. 9.4 based on a cylindrical model of a pulmonary capillary.
(a) Using continuity derive the relationship between the change in concentration of gas within the blood along the capillary and the ﬂux across the surface for a vessel of radius r and with a blood ﬂow rate f.
(b) Find the solution to this equation for the concentration of gas within the blood with distance along the capillary, x. Assume that the concentration at the inlet is c0 and that the concentration in the air space is constant along the length.
(c) The total gas ﬂux across the capillary surface can be calculated for a capillary of length L by integration. Using the solution from part (b) derive an expression for the total gas ﬂux.


<!-- ===== Page 133 ===== -->

122

9 The Respiratory System

(d) Calculate the ﬂux for a single capillary, assuming parameter values of: Cin À Co ¼ 1 mM; f ¼ 1 Â 10À13m3=s and 2prDsL ¼ 0:51 Â 10À13m3=s: Plot the variation of ﬂux with blood ﬂow rate, assuming that
all other parameters remain constant. (e) Using the result in part (d), explain why increasing the ﬂow rate has only
a small effect on the total ﬂux across the capillary wall. (f) What happens in the limit as L → ∞? What properties of the capillary
bed structure would ensure that this would be true?

9.2.2 Carbon Dioxide

Whilst the analysis above holds for the inert gases, where Henry’s law holds, the
metabolic gases are more complicated. CO2 is mainly transported within the red blood cells as HCOÀ3 ; the reaction being catalysed by the enzyme carbonic anhydrase:

CO2 þ H2O  H2CO3  HCOÀ3 þ H þ ;

ð9:5Þ

where CO2 combines with water to form carbonic acid, which then produces bicarbonate (HCOÀ3 ) and H+.

Exercise C
(a) Determine the rate constant for the second part of the reaction scheme for CO2 conversion to carbonic acid.
(b) Convert this to the ‘corrected’ rate constant assuming that almost all the available CO2 converts to carbonic acid.

In Exercise C you have derived an expression for the corrected rate constant, KA, that relates CO2 concentration to those of hydrocarbonate ions and H+. It is possible
to evaluate what difference this makes to the removal of CO2 from the capillary
blood in the lungs and arrive at the result:

Q ¼ f ð1 þ KAÞrCO2 ðp0 À pCO2 Þ;

ð9:6Þ

which is (1 + KA) larger than our result for inert gases in Eq. 9.5, with KA = 20 at a normal pH of 7.4. The conversion of CO2 to bicarbonate thus substantially increases the gas ﬂow rate, because as CO2 leaves the capillary by diffusion from


<!-- ===== Page 134 ===== -->

9.2 Gas Transport

123

the plasma it is rapidly replenished by more from the reversal of the bicarbonate reaction. Thus this is an example of facilitated diffusion that we met in Chap. 4.

Exercise D
(a) Starting with the model in Exercise B write down separate equations for the concentration of CO2 and HCOÀ3 in the capillary blood. Assume that you can ignore H2CO3 from your reaction scheme and thus have a single forward and backward reaction rate.
(b) Combine your equations from part (a) to give a single expression for the total concentration of CO2 and HCOÀ3 , i.e. CO2 in all its ‘forms’ for the purposes of transport.
(c) Using a quasi-steady state approximation write HCOÀ3 in terms of CO2 and thus derive the result in Eq. 9.6 using a similar analysis to Exercise B and considering the limit as L → ∞.
(d) If log10Ka = −6.1 calculate Kc at normal pH and thus comment on the effect of blood chemistry on CO2 removal from the body.

9.2.3 Oxygen

We have already seen in Chap. 1 that oxygen binds to haemoglobin the blood:

Hb þ 4O2  HbðO2Þ4;

ð9:7Þ

This is the primary means by which it is transported; a negligible fraction (3 %) is carried in solution in the plasma. Figure 9.3 shows the relationship between the partial pressure of O2 and haemoglobin saturation, which is highly non-linear. In theory the enhancement provided by haemoglobin on oxygen transport could be as much as 200, but in practice an enhancement of around 32 is achieved.

9.2.4 Tissue Gas Delivery
Delivery of gases to the tissues is essentially the reverse of the process in the lungs, and again the process is typically assumed to be perfusion limited. We can thus equate the amount of gas delivered to the difference in partial pressure between the arterial and venous ends of the capillary bed. This process can be modelled by a linear ﬁrst order differential equation, just as in Eq. 9.4:


<!-- ===== Page 135 ===== -->

124

9 The Respiratory System

Fig. 9.3 Saturation curves for haemoglobin (this ﬁgure is taken, without changes, from David Iberri under license: http://creativecommons.org/licenses/by-sa/3.0/)

dpt ¼ f rb ðpa À pvÞ; dt rt

ð9:8Þ

where pa, pa, and pt are the partial pressure in arterial blood, venous blood and tissue respectively, and we have to consider the solubility of the gas in both the blood and tissue.
This means that gas delivery can be thought of like the one-compartmental models we considered when we examined pharmacokinetics in Chap. 5. In this case the compartment is the tissue into which gas is being delivered and we assume that there is no spatial variation in the partial pressure in the tissue, thus the compartment is referred to as ‘well stirred’ or ‘well mixed’. This can be represented graphically as in Fig. 9.4, where a number of other simple models of tissue-capillary gas exchange are shown that extend the model by accounting for some degree of diffusion limitation.
The one compartment model means that the tissue concentration will respond exponentially to a change in gas concentration and a time constant can be determined for that process; often the half-life is quoted. This will vary from tissue to tissue depending upon the solubility, but more signiﬁcantly upon the perfusion rate. Given the range of tissues and accompanying perfusion rates, simple models often divide the body into a collection of compartments with a range of representative time constants.
As before, this description is ﬁne for the inert gases, but is insufﬁcient for the metabolic gases. As we have already seen, binding in the blood gives a non-linear


<!-- ===== Page 136 ===== -->

9.2 Gas Transport

125

(a) (b) (c) (d) (e)

Fig. 9.4 Compartmental models of tissue gas exchange (reproduced with permission, M.A. Chappell, DPhil thesis, University of Oxford, 2006)
relationship between concentration and partial pressure. There is further binding of oxygen in the tissues to myoglobin (Mb), whose saturation curve is much like the standard Michaelis–Menten function rather than the sigmoidal shape of haemoglobin. The difference between these two curves arises from the greater afﬁnity of myoglobin for oxygen which means oxygen is readily transferred from haemoglobin to myoglobin, improving the transfer rate from blood into tissue. The presence of myoglobin in muscles also provides some limited oxygen store and accounts for the colour of red meats.
A further aspect for the behaviour of the metabolic gases is that oxygen is consumed in the tissues and carbon dioxide is being produced, requiring an additional metabolism term in the equation above. If we are interested in the total pressure of gas in solution in the tissue it is often a reasonable approximation to assume zero dissolved oxygen in tissue, because oxygen is rapidly metabolised (or bound), and an equivalent ﬁxed fraction for the CO2 that has been produced.


<!-- ===== Page 137 ===== -->

126
9.2.5 Blood Oxygenation

9 The Respiratory System

The standard measurement of blood oxygenation is the fraction of the carrying capacity of the blood that is being used: the oxygen saturation. Pulse-oximetry is a widely used method for measuring the oxygen saturation of the blood. The sensor is placed in a thin part of the body, for example a ﬁngertip or earlobe. It works by passing two distinct wavelengths of light through the body to a photodector; the relative absorbance at the two wavelengths allows the oxygen saturation of arterial blood to be determined.
The measurement relies upon the changes in colour of haemoglobin with oxygen saturation, thus pulse-oximetry strictly measures the percentage of haemoglobin that is loaded with oxygen. Since, as we have seen, haemoglobin is the main carrier of oxygen in the blood, this in turn is a good measure of oxygen saturation of the blood. Figure 9.5 shows the absorption spectra for both oxy- and deoxyhaemoglobin.
Pulse oximetry works in the Near Infrared Region (NIR) of the light spectrum and exploits the distinctive differences in absorption seen in this region. Typically two wavelengths, 660 and 940 nm, are used and are sampled up to 30 times per second allowing changes in ambient light and also the amount of arterial blood present to be corrected for. Once the ratio of light transmission at the two wavelengths has been calculated this can be converted to oxygen saturation, which in normal healthy individuals will be above 95 %.
Whilst pulse oximetry is widely used for the measurement of oxygen saturation, the time course associated with the measurement of optical transmission, the photoplethysmogram (PPG), is less widely used. This signal captures the time varying blood volume in the skin associated with the differences between systolic and diastolic pressure in the arteries. Thus it is possible to monitor heart rate from the PPG. It is also, theoretically, possible to monitor respiration, since changes in lung volume and that of the thoracic cavity affect the heart. This leads to small

Fig. 9.5 Absorption spectra for Oxy- and deoxy-haemoglobin, showing the Near Infrared Region (this ﬁgure is taken, without changes, from Adrian Curtin under license: http:// creativecommons.org/ licenses/by-sa/3.0/)


<!-- ===== Page 138 ===== -->

9.2 Gas Transport

127

changes in systolic and diastolic pressure during the breathing cycle that might be
detected from the PPG. Measuring such small changes is challenging, but has not prevented attempts to measure vital signs using the light reﬂected from exposed
areas of skin acquired using conventional digital video cameras.

9.2.6 Control of Acid-Base Balance

One further aspect of the body’s behaviour that we will consider here is the reg-
ulation of the acid-base status. The maintenance of the pH of arterial blood between
7.35 and 7.45 is absolutely vital for the correct functioning of the human body. The most important inﬂuence on pH is the transport of CO2 in the blood. The reaction equation that governs buffering is the same one we considered for CO2 transport above. The expression for the ‘corrected’ rate constant can be re-arranged into the
form:

ÂHCO3ÀÃ pH ¼ pKA þ log10 ½CO2 ;

ð9:9Þ

where pH ¼ À log½H þ  and pKA ¼ À logðKAÞ ¼ 6:1: This is the Henderson– Hasselbach equation. The concentration of CO2 is approximately proportional to the partial pressure of CO2. The fact that the concentrations of both bicarbonate and carbon dioxide can be independently controlled, by the kidneys and the lungs respectively, means that it proves relatively straightforward to maintain pH at a constant level. This is achieved by the autonomic nervous system that we will meet in Chap. 10.

Exercise E
(a) Derive the Henderson–Hasselbach equation from the ‘corrected’ equilibrium constant in Exercise C.
(b) Given that the concentration of CO2 can be linearly related to the partial pressure of CO2, with an Ostwald constant of 0.03 mM/mmHg, calculate the pH value for a partial pressure of 40 mmHg and a concentration of bicarbonate of 24 mM.
(c) Draw lines of constant pCO2 (20, 40 and 60 mmHg) on a plot of bicarbonate concentration versus pH. Use a range of pH of 7.1–7.7 and bicarbonate concentration of 10–40 mM and illustrate the point calculated in part (b).
(d) If the pCO2 rises from 40 to 60 mmHg (why might this happen?), how can the body maintain a constant pH?


<!-- ===== Page 139 ===== -->

128
9.3 Conclusions

9 The Respiratory System

In this chapter we have looked at the structure of the respiratory system and especially the respiratory circulation. We have used models of transport from earlier chapters to explain the unique structure of the lungs that enables effective gas exchange. You should now be able to setup compartmental models for gas transport and analyse these for inert and metabolic gases using suitable approximations.


<!-- ===== Page 140 ===== -->

Chapter 10
The Central Nervous System

We have so far looked at a number of the most vital systems in the body. However, their actions and interactions all need to be coordinated and this role falls to the nervous system, which we will brieﬂy look at in this ﬁnal chapter. The nervous system can be divided into two parts:
• The central nervous system (CNS): the brain and spinal cord. • The peripheral nervous system (PNS): nerves (bundles of nerve cells) con-
necting the CNS to other parts of the body. The PNS also encompasses the enteric nervous system, a semi-independent part of the nervous system responsible for the gastrointestinal system.
Figure 10.1 shows a conceptual model of how this all ﬁts together. Notice that we have both inputs (afferents) and outputs (efferents), but also a division into parts of which we are consciously aware and have direct control: the somatic nervous system, and the parts that we are largely unaware of and happens automatically— the autonomic nervous system.

10.1 Neurons

We have already met the idea of a neuron or nerve cell in Chaps. 3 and 4 where we considered the action potential and chemical synapses. Neurons are the main actors in the CNS, providing a way to transmit both efferent and afferent signals to and from the CNS. A number of specialized neurons exist:

• Sensory neurons: These respond to stimuli such as light and sound in the sensory organs and send this information back to the CNS.
• Motor neurons: These receive signals from the CNS and cause muscle contraction or affect glands (for the release of hormones).
• Interneurons: These connect neurons to other neurons within the same region of the CNS.

Typically a neuron will have a cell body, dendrites and an axon, as shown in Fig. 10.2. The dendrites are thin structures arising from the cell body that typically

© Springer International Publishing Switzerland 2016

129

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3_10


<!-- ===== Page 141 ===== -->

130

10 The Central Nervous System

Fig. 10.1 Conceptual diagram of the nervous system
Fig. 10.2 Schematic of a typical CNS neuron (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
branch multiple times, forming a complex ‘dendritic tree’. In contrast the axon (and there is only ever a single axon) is a special extension of the cell body that may extend as far as 1 m. The axon itself may branch hundreds of times before it terminates at the dendrite of another neuron. At the majority of synapses signals are sent from the axon of one neuron to the dendrite of another, although there are exceptions to this rule. It is the axon that carries signals over long distances and is thus insulated with a myelin sheath that in turn is interrupted at various points by the nodes of Ranvier to aid conduction of the action potential as we saw in Chap. 4.


<!-- ===== Page 142 ===== -->

10.2 Autonomic Nervous System

131

10.2 Autonomic Nervous System

There are a great many systems in the body that the CNS needs to regulate over which we have no (or very little) direct conscious control. These include the regulation of digestion, maintaining glucose balance and regulating heart rate. The autonomic system is divided into sympathetic and parasympathetic parts, as shown in Fig. 10.3. Most organs receive signals from both and broadly the role of the sympathetic system is to put the organ into ‘emergency mode’, whereas the parasympathetic system has the opposite effect of placing the organ into ‘vegetative mode’. The connection between the CNS and PNS for the autonomic nervous system occurs primarily in the spinal cord, but the bodies of the nerve cells largely reside in ganglia that are distributed around the body.

10.2.1 Autonomic Control of the Heart
The control of the cardiovascular system is, unsurprisingly, a highly complicated topic and we will only look at a few parts of this system. We will focus on the

Fig. 10.3 The autonomic system showing sympathetic and parasympathetic parts separately (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons. org/licenses/by/3.0/)


<!-- ===== Page 143 ===== -->

132

10 The Central Nervous System

baroreceptor and chemoreceptor reﬂexes in the context of maintaining cardiac output, but there are many other components to the control of the cardiovascular system that act to maintain other parameters such as blood volume. The aim here is just to give you a brief introduction to how the body maintains homeostasis through measuring physiological parameters, feeding back this information to the brain and acting on it in a co-ordinated manner. This is just like any engineering control system, where feedback based on measurements is used to control a system and hence to maintain equilibrium.
There are three cardiovascular centres in the medulla oblongata in the brain. These neurons respond to changes in blood pressure, blood gas concentrations and pH. The cardioaccelerator centre acts to increase cardiac function through sympathetic activation and the cardioinhibitor centre acts to reduce cardiac function through parasympathetic activation, whilst the vasomotor centre controls vessel wall stiffness via smooth muscle cells.

10.2.2 Cardiac Efferents
The cardiac muscle cells are the main efferents in the heart. As we have seen, their regular contraction is self-sustaining, coordinated by the SAN and requires no external instruction to maintain a resting heart rate. The heart is thus a good example of the competing role of sympathetic and parasympathetic nerves and how these are used to tune the heart rate, as illustrated in Fig. 10.4:
• Parasympathetic stimulation: Synaptic terminals release the neurotransmitter ACh; this slows the rate of depolarization during the pacemaker potential of the SA node, thus increasing the interval between successive action potentials, and slowing the heart rate. ACh acts by increasing potassium permeability, keeping the membrane potential nearer to that of potassium, retarding the growth of the pacemaker potential toward the threshold for triggering action potentials.
• Sympathetic stimulation: Synaptic terminals release norepinephrine. This speeds the heart rate and increases the strength of contraction, an effect which is mediated by an increase in calcium permeability. The greater the number of calcium channels that are open, the lower the threshold is for triggering an AP in the SA, thus increasing the heart rate. In the cardiac muscle cells the increase in calcium permeability increases the calcium inﬂux during the plateau, increasing the strength of contraction.
In both cases the effects of the neurotransmitter are indirect, unlike those we saw when we looked at chemical synapses where the neurotransmitter acted directly on the ion channels. Note that this means that the body can, via an indirect mechanism, effect longer term changes without having to provide a continuous neural signal.


<!-- ===== Page 144 ===== -->

10.2 Autonomic Nervous System

133

Fig. 10.4 Effects of parasympathetic and sympathetic activity on heart rate (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
10.2.3 Cardiac Afferents
The baroreceptor reﬂexes are rapid mechanisms that attempt to minimise short-term ﬂuctuations in blood pressure. Baroreceptors are nerve endings in the walls of the carotid sinus, where the external and internal carotid arteries split, and in the aortic arch. They are termed mechanoreceptors as they are sensitive to


<!-- ===== Page 145 ===== -->

134

10 The Central Nervous System

Fig. 10.5 Baroreceptor control of blood pressure
stretching of the arterial wall, which is related to arterial blood pressure. When there is a drop in blood pressure, resulting in a reduction in wall stretch, the ﬁring rate of the receptors is reduced.
This feeds back to the brain and results in an increase in heart rate and stroke volume: as a result, there is an increase in blood pressure. This increase in heart rate is known as tachycardia (the opposite, a reduction in heart rate, is known as bradycardia). How this works is shown in terms of a control loop (with the large arrows used to describe complex relationships) in Fig. 10.5: a decrease in ABP results in a decrease in baroreceptor ﬁring rate, an increase in cardiac output, which, coupled with vasoconstriction, results in an increase of ABP and a return to baseline conditions. There are also many other processes that act to maintain homeostasis in the longer term.
The carotid sinus receptors respond to pressures of approximately 60–180 mmHg, whilst the aortic arch receptors are less sensitive as they have a higher threshold pressure. The maximal sensitivity is around normal ABP. The receptors are also sensitive to the rate of change of ABP, and increases in the pulse pressure make the baroreceptors more sensitive to changes in MAP. The baroreceptors quickly adapt to changes in the mean level of MAP: if the level drops for a sustained period, unaltered by the action of the baroreceptors, the reﬂex will gradually reset itself to this new operating point over a period of several hours. They are thus only short-term regulators of MAP.
The chemoreceptor reﬂexes originate in the aortic arch and carotid bodies and respond to changes in arterial oxygen and carbon dioxide levels. If blood pressure drops and oxygen levels in the blood decrease, the chemoreceptor reﬂexes will respond by increasing sympathetic activity. This increase acts in the same way as a decrease in parasympathetic activity and so heart rate increases.
10.3 Somatic Nervous System
We will now focus on the somatic nervous system. Remember that this is the part of the CNS whose inputs, neuronal afferents, we are largely conscious of and whose outputs or actions, neuronal efferents, we generally have voluntary control of.
The familiar patellar (knee-cap) reﬂex provides a good example of the somatic nervous system in action. A simpliﬁed diagram of the circuitry involved in this reﬂex is shown in Fig. 10.6. Concentrating only on the quadriceps muscle to start


<!-- ===== Page 146 ===== -->

10.3 Somatic Nervous System

135

Fig. 10.6 Patellar reﬂex (this ﬁgure is taken, without changes, from Backyard Brains under license: http://creativecommons.org/licenses/by/3.0/)
with: tapping the knee causes a stretch in the muscle ﬁbres that stimulates an action potential in stretch-sensitive sensory neurons. This signal is passed to the spinal cord arriving at a synapse with the motor neuron. This then elicits an action potential in the motor neuron, which is carried back to the muscle arriving at a neuromuscular synapse as described in Chap. 4. The resulting AP causes contraction of the muscle ﬁbre, which when repeated across the whole muscle causes contraction of the quadriceps muscle and the resulting leg extension.
10.3.1 Temporal and Spatial Summation of Synaptic Potentials
The neuromuscular junction is unusual in one respect, in that a single AP that arrives at the presynaptic side leads to a sufﬁciently large depolarization on the post synaptic side to trigger an AP there. Thus such a synapse is called a ‘one-for-one’ synapse. However, most synapses are not that strong: a single presynaptic AP will cause only a small depolarization of the postsynaptic cell, called an excitatory postsynaptic potential (epsp). The synapse between a single starch receptor and the quadriceps motor neuron in the patellar reﬂex is a typical example of this.


<!-- ===== Page 147 ===== -->

136

10 The Central Nervous System

Each epsp is of the order of 1 mV, far smaller than the 10–20 mV threshold required. However, if several subsequent epsp arrive before the effects of the previous ones have died away a sufﬁcient depolarization of the postsynaptic cell can be achieved. This is called temporal summation. An alternative mechanism by which epsp can sum to reach a threshold is via the postsynaptic cell receiving multiple presynaptic inputs, this is called spatial summation. This relies on the fact that most neurons are connected to many others via their dendrites. Both temporal and spatial summations are involved in the patellar reﬂex.

10.3.2 Excitatory and Inhibitory Synapses
So far we have only met excitatory synapses where the AP in the presynaptic cell causes a depolarization in the postsynaptic cell. However, it is also common to ﬁnd inhibitory synapses, where the release of neurotransmitter due to the presynaptic AP tends to prevent the ﬁring of the postsynaptic AP. In this case the neurotransmitter causes a hyperpolarization of the post synaptic cell, making the membrane potential more negative and moving it further way from the threshold required to elicit an AP. Thus we now also have a class of inhibitory postsynaptic potential (ipsp). Like the epsp we have already met, the ipsp is achieved through changes in the ionic permeability of the postsynaptic cell membrane.
One possible mechanism for an ipsp would be an increase in the permeability to K+ similar to the undershoot we met in Chap. 3. Many inhibitory synapses, however, rely on changes in Cl− permeability. In many neurons chloride pumps maintain the chloride equilibrium potential more negative than the membrane potential, thus an increase in Cl− permeability leads to a hyperpolarization of the neuron. Even when the Cl− equilibrium potential is near to that of the membrane potential, inhibition can occur, as, although there will be no appreciable hyperpolarization, the increase in Cl− permeability will resist any increases in the membrane potential brought about by an excitatory input.
Figure 10.7 shows an example of summation of epsps and ipsps that have been received by a neuron. At time A the sum effect of a series of epsps has been insufﬁcient to initiate an action potential in the axon. By time B sufﬁcient epsps have been received within a short enough time to reach threshold and an action potential will be generated and will propagate along the axon.
The combination of inhibitory and exhibitory synapses plays an important role in the patellar reﬂex. In Fig. 10.6 we also have to consider the ﬂexor muscles at the back of the thigh as well as the quadriceps muscle. As the leg extends, this will cause a stretch in these muscles that in turn will, via the excitatory pathway through the spinal cord, cause contraction of the ﬂexor muscle, jerking the leg back again. In turn this would elicit a stretch and contract reaction from the quadriceps muscle and so it would go on. However, the extra inhibitory link between quadriceps sensory neuron and the ﬂexor’s motor neuron prevents this occurring and only the ﬁrst extension is seen.


<!-- ===== Page 148 ===== -->

10.3 Somatic Nervous System

137

Fig. 10.7 Summation of postsynaptic potentials (this ﬁgure is taken, without changes, from OpenStax College under license: http://creativecommons.org/licenses/by/3.0/)
10.3.3 The Brain
The ‘pinnacle’ of the nervous system is the brain, where many millions of individual neurons interact via a complex network of dendritic connections and synapses. This relies upon the many combinations that are possible when we bring many epsp and ipsp together with temporal and spatial summation over a densely connected neural network.
The brain can broadly be considered to contain both ‘grey matter’ and ‘white matter’ reﬂecting different visual qualities of the tissue, Fig. 10.8. These actually primarily represent a division of the brain into neurons in the grey matter that constitutes a thin layer with a large surface area that takes the form of a highly
Fig. 10.8 Image of the brain collected using MRI showing folded structure and division into grey and white matters (reproduced with permission, M.A. Chappell)


<!-- ===== Page 149 ===== -->

138

10 The Central Nervous System

folded sheet within the head, and in the white matter bundles of axons from neurons carrying APs to different regions of the brain and out of the brain. Within the brain there is also another sort of cell called glial cells of which there are a number of different types, all of which provide supporting roles either structurally or metabolically to the neurons.

10.3.4 Function: Introduction to EEG and FMRI
The complexity of the CNS and the brain in particular makes it both very difﬁcult to study and one of the most studied parts of the human body. It is possible to make measurements of neural activity, however, not with a resolution that allows individual cells to be investigated. Like the ECG of the heart that we met in Chap. 7, electroencephalography (EEG) measures electrical signals in the brain using an array of electrodes placed on the head. Alternatively, magnetoencephalography (MEG) can be used to detect magnetic ﬁelds arising from electrical activity of the brain with highly sensitive magnetic detectors. Both methods provide very highly sampled temporal information about signals in the brain, but provide low spatial resolution, since it is difﬁcult to reconstruct spatial locations from an array of measurements made outside of the head.
Very many EEG electrodes or MEG detectors can be placed across the head to try to localise electrical activity to different areas of the brain. In the heart the main electrical activity arose from the propagation of the AP across the heart wall, which gave rise to a relatively strong and highly directional vector potential. In the brain many APs are occurring that are not necessarily so simply co-ordinated, although, due to the structure of the brain, the main direction of travel is perpendicular to the skull. Despite the complexity of the signals in the brain, even with just a few electrodes placed around the head, it is possible to measure signals in speciﬁc bands of frequencies that reﬂect levels of co-ordination in the signalling in the brain’s nervous network.
Magnetic Resonance Imaging (MRI) methods have also been used to study brain activity, typically called functional MRI (fMRI). The most common method is to exploit the Blood Oxygen Level Dependent (BOLD) effect. BOLD relies upon the different magnetic properties of oxygenated and deoxygenated blood, allowing increases in oxygen usage to be indirectly measured from changes in perfusion and blood volume in the brain during a task compared to that during rest. This method provides far better spatial resolution, of the order of mm, than EEG or MEG, but with much poorer temporal resolution, typically one measurement every few seconds. Much research using these methods has allowed the functions of various different regions of the brain to be identiﬁed and increasingly their connections to each other are being explored.


<!-- ===== Page 150 ===== -->

10.4 Conclusions

139

10.4 Conclusions

In this chapter we have examined the nervous system and seen how the concepts of action potentials and their propagation come together to regulate the body as part of the autonomic system and provide for conscious and voluntary action through the somatic system. We have seen that through the summation of many action potentials the brain is a very complex organ, requiring in turn a very speciﬁc structural architecture and metabolic support system. Finally, despite the complexity of the brain we have seen that we are still able to measure at least some of its functionality by examining electrical and metabolic changes.
At the end of this chapter we have completed our introductory survey of physiology from an engineering perspective. We started with the fundamental unit of living matter, the cell, and examined behaviour associated with it. We then started to examine larger systems where we might bring cells together into the form of a tissue, and then how groups of tissues form systems. Finally, we examined some of the most important systems in the body. You will hopefully have learned a lot about how the human body works, although we have only scratched the surface. More importantly you will have seen that a very wide range of engineering methods can be used to understand and study physiology, bringing interest to engineering and beneﬁt to medicine.


<!-- ===== Page 151 ===== -->

Answers

1. Cell structure and biochemical reactions A Reaction equations:

da ¼ kÀcd À k þ ab2 dt db ¼ kÀcd À k þ ab2 dt dc ¼ k þ ab2 À kÀcd dt dd ¼ k þ ab2 À kÀcd dt

In steady state this gives the result in A.2.

B

(a) Reaction equations

da ¼ kÀ1cd À k þ 1ab dt dc ¼ kÀ2ef À k þ 2c dt

(b) In steady state this gives the result in B.3. C Equilibrium approximation:

© Springer International Publishing Switzerland 2016

141

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3


<!-- ===== Page 152 ===== -->

142

Answers

kÀ1c ¼ k þ 1se

Ksc ¼ sðeo À cÞ

c ¼ eo s Ks þ s

V ¼ dp ¼ k þ 2c ¼ k þ 2eo s

dt

Ks þ s

Quasi-steady-state approximation

ðk þ 2 þ kÀ1Þc ¼ k þ 1se

Kmc ¼ sðeo À cÞ

c ¼ eo s Km þ s

V ¼ dp ¼ k þ 2c ¼ k þ 2eo s

dt

Km þ s

Since Km [ Ks; the reaction velocity is always smaller for the quasi-steady-state approximation.

D This is known as the double reciprocal form:

1¼ K 1þ 1 V Vmax s Vmax

If we plot 1/V against 1/s, we get a straight line. This intercepts the x axis when 1=s ¼ À1=K and the y axis when 1=V ¼ 1=Vmax.

E

(a) Using a logarithmic transformation, we get:





V ln

¼ n ln s À n ln K

Vmax À V



(b)

If we plot ln

V Vmax ÀV

against ln s, we get a straight line. This intercepts



the

x axis when

ln s ¼ ln K

and the

y axis

when

ln

V Vmax ÀV

¼ n ln K.

Plotting the values given yields values of n ¼ 2:394 and K ¼ 1:5 mM/s.

Yes it is a good ﬁt.

F

(a) Quasi-steady-state approximation:


<!-- ===== Page 153 ===== -->

Answers

143

k þ 1se ¼ ðk þ 2 þ kÀ1Þc1

k þ 3ie ¼ kÀ3c2





e s þ i þ 1 ¼ eo

Km Ki

V ¼ dp ¼ k þ 2c1 ¼ k þ 2  eo  s ¼

Vmaxs

dt sKm þ iKi þ 1 Km Kmð1 þ i=KiÞ þ s

(b) As the inhibitor increases, the curve shifts to the right. The intercepts on the double reciprocal plot would only be affected on the x axis, where the intercept would move to the right (i.e. towards the origin).
2. Cellular homeostasis and membrane potential
A
(a) V ¼ V0: The concentrations of P and Q are the same inside and outside, this is the isotonic case and the cell is already in equilibrium for concentrations and thus the volume stays the same as the original.
(b) V ¼ 2V0: We require that [P] = [Q] in equilibrium, but we have initially ½P0¼ 2½Q0; i.e. a hypertonic osmotic imbalance. Given that the volume of solution outside the cell is far larger than the cell itself (effectively inﬁnite) the concentration of Q is not going to change, thus water must move into the cell to dilute P: to halve the concentration inside we need to double the volume. Formally, we require ½P=V ¼ 50; initially we have ½P0=V0 ¼ 100; solving for V ¼ 2V0:
B
The cell will expand indeﬁnitely: the only way that the two requirements of equal internal and external concentration of Q and equal total concentration can be met is for the concentration of P to be zero, the cell expands to inﬁnite size. Formally, we have two equilibrium equations:
½Qi ¼ ½Qe ½Pi þ ½Qi ¼ ½Qe
where the subscripts i and e refer to the internal and external environments respectively. The only solution is ½Pi¼ 0:
C
(a) V ¼ V0 We have two equilibrium equations: Concentration balance for R:


<!-- ===== Page 154 ===== -->

144

Answers

½Ri¼ ½Re
Total concentration (osmolarity):
½Pi þ ½Ri¼ ½Qe þ ½Re
These equations are satisﬁed with the initial concentrations so the system is in equilibrium. (b) V ¼ 2 V0: We have the same two equilibrium equations as in part a), but the system is not initially balanced. However
• the total amount of P is ﬁxed inside the cell • the concentrations of Q (outside the cell) is ﬁxed • the concentration of R both inside and outside the cell is ﬁxed, since
the external concentration will not be altered by movement of R into the cell (at least to the same degree as the internal concentration) and R is free to move in and out of the cell. Writing the balance of total concentration in terms of quantities of P and R and the ﬁnal volume:
P/V þ R/V ¼ 50 þ 100
Concentration of R is ﬁxed:
R/V ¼ 100
Thus:
P/V ¼ 50
Since P0 ¼ 100 V0 then V ¼ 2 V0:
D
(a) Yes (b) This example is a bit different to the cell examples so far, in that we have
a closed system - the external concentration is not ﬁxed. We are also examining a system in which water isn’t permeable - so we do not need to consider osmolarity and there are no other permeable uncharged species. Using conservation of mass, since the volume is ﬁxed this is the same as considering the total concentrations of these species:


<!-- ===== Page 155 ===== -->

Answers

145

½K þ l þ ½K þ r ¼ 700 mM ½ClÀl þ ½ClÀr ¼ 300 mN
Charge neutrality: ½K þ lÀ½ClÀlÀ2ÂX l 2ÀÃ ¼ 0 ½K þ rÀ½ClÀr ¼ 0
Gibbs-Donnan:
½K þ rÂ½ClÀr¼ ½K þ lÂ½ClÀl
Solving these equations gives the following equilibrium concentrations
½K þ r ¼ 210 mM ½K þ l ¼ 490 mM ½ClÀr ¼ 210 mM ½ClÀl ¼ 90 mM ½X2Àl ¼ 200 mM

(c) To achieve the correct concentration and electrical gradients for Cl- leads to changes in the K+ concentrations to the left and right of the membrane. As the left gets more negative and the right more positive due to Cl- ion movement, K+ has to migrate to the left to guarantee charge neutrality on eitherside. 
þ
(d) EK ¼ 58 mV Â log ½K þ  ½K r ¼ À21:34 mV l
E
(a) Concentration balance:
a þ b þ c þ 108 ¼ 120 þ 5 þ d
Charge balance (both inside and outside)
a þ b ¼ c þ 108 Â 11 9
120 þ 5 ¼ d


<!-- ===== Page 156 ===== -->

146
Gibbs-Donnan equilibrium: bc ¼ 5 Â 125

Answers

(b) For potassium ions: ½K þ o
EK ¼ 58 mV Â log þ ¼ À81 mV ½K i
For chloride ions ½ClÀo
ECl ¼ À58 mV Â log À ¼ À81 mV ½Cl i
As expected they are equal and the membrane potential is −81 mV. (c) For sodium ions:
½Na þ o ENa ¼ 58 mV Â log þ ¼ þ 58 mV
½Na i

F (a) Using the Nernst equation:

Ion

Equilibrium potential (mV)

Na+

+67

K+

−90

Cl−

−34

Ca2+

+118

This is not in equilibrium since they not equal. This means that the membrane potential will fall somewhere in between the extremes and be determined also by permeability.


<!-- ===== Page 157 ===== -->

Answers

147

(b) Total concentration (osmotic) balance: 10 þ 140 þ 30 þ 10À4 þ ½P ¼ 145 þ 4 þ 114 þ 1:2 ½P ¼ 84:2 mM

Internal charge balance: 10 þ 40 À 30 þ 2 Â 10À4 þ Z Â ½P ¼ 0
Z ¼ À1:43 (the net charge on the internal proteins etc). (c) External charge balance:
145 þ 4 À 114 þ 1:2 6¼ 0

The cell cannot be in a steady state in this case as electrical neutrality outside the cell is not met. 3. The Action Potential A
Em ¼ þ 47:5 mV:

B The total current ﬂowing from inside to outside, Iapp; is the sum of the four branches. For sodium: the current of sodium ions arises from the difference in potential between the sodium equilibrium and the membrane potentials ðEm À ENaÞ and this passes through the membrane subject to a conductivity (1/resistance) of gNa; using Ohm’s law:
iNa ¼ gNaðEm À ENaÞ:
Likewise for potassium and the ‘leakage’ current:
iK ¼ gK ðEm À EK Þ; iL ¼ gLðEm À ELÞ:
The membrane acts like a capacitor and thus current ﬂow in response to changes in membrane potential can be described by:
im ¼ Cm dEm : dt


<!-- ===== Page 158 ===== -->

148

Answers

Summing:

Iapp ¼ gK ðEm À EK Þ þ gNaðEm À ENaÞ þ gLðEm À ELÞ þ Cm dEm : dt

Re-arranging gives:

Cm dEm ¼ ÀgK ðEm À EK Þ À gNaðEm À ENaÞ À gLðEm À ELÞ þ Iapp: dt

C (a) The two equations are:

dO ¼ aC À bO; dt dC ¼ ÀaC þ bO: dt

(b) The sum of the probabilities is 1. Hence: dO ¼ að1 À OÞ À bO: dt

(c) The steady state value and time constant are:
O ¼ a=ða þ bÞ; sO ¼ 1=ða þ bÞ:

D
(a) This is just a substitution of Equations 3.3–3.5 into the expressions from Exercise C for each of the gates in turn.
(b) In the steady-state with the potential at zero (remember that this is relative to the reference value), the h gates are largely open and the m and n gates largely closed, this requires bm ) am and bh ( ah: When the voltage increases, the gates go from open to closed and vice versa. The time constants for the n and h gates are much larger than for the m gate, so the m gate responds much more rapidly, as expected, this requires bm ( am and bh ) ah:
E
About 2.3 μA.E


<!-- ===== Page 159 ===== -->

Answers

149

F

(a) If the permeability to K+ is high compared to other ions then EK+ will dominate the membrane potential. From exercise 2F we know that EK+ is −90 mV so the range suggested seems reasonable.
(b) From the ﬁgure the membrane potential plateaus at +52 mV. If, as suggested, we ignore the other ions and assume that Ca2+ permeability
dominates then we need ECa2þ equal to or greater than +52 mV:

ECa2 þ ¼ 58 mV log10 2

!

Â 2 þ 1:2 Ã Ca i

! þ 52 mV:

This requires that ÂCa i 2 þ Ã 0:019 mM:

4. Cellular Transport and Communication

A

Starting with the diffusion equation in 1-dimension:

@c

@2c

¼ f þD 2:

@t

@x

We are looking for transport in the steady state, thus changes with respect to time are zero. We will also assume there is no generation (or consumption) of the species within the membrane thus f=0:

@2c D 2 ¼ 0:
@x

This is a standard second order differential equation with a solution of the form c=ax+b. The boundary conditions from the diagram are:

cðx ¼ 0Þ ¼ co; cðx ¼ LÞ ¼ ci:

Hence c ¼ co þ ðci À coÞ x : L
Using Fick’s law we can write the ﬂux: J ¼ D @c ¼ D ðci À coÞ: @x L


<!-- ===== Page 160 ===== -->

150

Answers

If we were to account for relative solubility via the partition coefﬁcient then the boundary conditions would change - since the concentration at the boundaries inside the membrane would be higher (or lower) compared to the same boundary outside the membrane:

cðx ¼ 0Þ ¼ Kco: cðx ¼ LÞ ¼ Kci:

The solution would look like:

B
The differential equations for this process are:
dpi ¼ kpe À kpi þ k þ sici À kÀpi; dt dpe ¼ kpi À kpe þ k þ sece À kÀpe; dt dci ¼ kce À kci þ kÀpi þ k þ sici; dt dce ¼ kci À kce þ kÀpe À k þ sece: dt
C
(a) This constant current source can equally well be simulated in the equations by an increase in the resting potential for potassium, since both contribute a ﬁxed term on the right hand side of the equation. A change in equilibrium potential is directly related to concentration via the Nernst equation. The necessary rise in potassium equilibrium potential is:
mK ¼ gKn4 Iapp ¼ 36 Â 0:31774 2:3 ¼ 6:27 mV:
(b) Relating the potassium concentration to potential by the Nernst equation, the relative change in extracellular potassium is given by:


<!-- ===== Page 161 ===== -->

Answers

151

À½K þ o new Á ¼ À½K þ o old Á 10ð6:27=58Þ ¼ 1:28À½K þ o old Á :

A similar approach for sodium gives a factor of over 500, which is not physiologically possible!
D (a) The current ﬂowing in the membrane is given by:

i þ @i dx À i ¼ Cmcdx @V þ cdx V;

@x

@t Rm

where c is the circumference of the cell wall. The potential difference within the segment of cell is:

V þ @V À V ¼ iRc: @x

Combining these gives Eq. 4.12.
(b) Assuming a circular cell cross section: if rm and cm are given for a unit area of membrane then Rm ¼ rm=ðpdÞ and Cm ¼ cmpd:; if rc is given for a unit area of cytoplasm tens Rc ¼ 4rc=ðpd2Þ. Therefore:

sm ¼ rmcm: rﬃﬃﬃﬃﬃﬃﬃ
km ¼ rmd: 4rc

(c) sm ¼ 8:4 ms and km ¼ 0:15 cm. (d) This is a second order differential equation in x with solution (including
boundary condition at x = 0) of: V ¼ 100eÀx=k: Solving for x when V = 20 mV gives x = 2.4 mm.
5. Pharmacokinetics
A
(a) Starting with:

Vc dCp ¼ ÀVckeCpðtÞ þ AinðtÞ: dt

Take Laplace transform: sVcCpðsÞ ¼ ÀVckeCpðsÞ þ AinðsÞ:


<!-- ===== Page 162 ===== -->

152

Rearrange

CpðsÞ ¼ 1 AinðsÞ : Vc ðs þ keÞ

Inverse Laplace transform (using convolution property)
Zt CpðtÞ ¼ 1 AinðkÞeÀkeðkÀtÞdk:
Vc
0

Answers

(b) AinðtÞ ¼ k0

k0eÀket Z t kek

CpðtÞ ¼

e dk;

Vc

0

k0eÀket

CpðtÞ ¼

ðeket À 1Þ;

Vcke

CpðtÞ ¼ k0 À1 À eÀketÁ: Vcke

(c) The steady state concentration can be found in the limit t ! 1 Cp1 ¼ k0 : Vcke

As might be expected this concentration depends on the relative rate of elimination and delivery, as well as the volume of distribution into which the substance is dissolved.

B (a) Starting with:

dAa ¼ ÀkaAaðtÞ þ AinðtÞ; dt dAp ¼ kaAaðtÞ À keApðtÞ: dt

Laplace transform (with zero initial conditions):
AaðsÞ ¼ AinðsÞ ; s þ ka
ApðsÞ ¼ kaAaðsÞ : s þ ke


<!-- ===== Page 163 ===== -->

Answers

153

Thus:

ApðsÞ ¼ kaAinðsÞ : ðs þ keÞðs þ kaÞ

Inverse Laplace Transform: ApðtÞ ¼ ka ÀeÀket À eÀkatÁ Ã AinðtÞ: ka À ke
AinðtÞ ¼ D Ã dðtÞ; where D is the dose. Also Ap ¼ Cp ÃVc : CpðtÞ ¼ D ka ÀeÀket À eÀkatÁ: Vc ka À ke

(b) A sum of a growth toward saturation plus a decay toward zero leads to something that ﬁrstly increases and then decays away.
(c) The slowest time constant, which we would expect to be elimination, will dominate at later time points and thus a straight line ﬁt to the log values will give an estimate for this time const.
C
(a) Using the data in the table we need to calculate the area under the curve for both methods of administration. Trapezoidal integration will sufﬁce for this calculation. We do not have measurements at very long time post-administration so we do not know when the concentration drops to zero, we will ignore any concentration after the last time point:
F ¼ AUCoral ¼ 251:07 ¼ 0:650 AUCIV 386:04
(b) We can use the IV injection to quantify the elimination kinetics, it will obey Equation 5.6. We can estimate the parameters either from a semi-logarithmic plot of concentration versus time, which gives a straight line slope of −0.500 and intercept of 5.298, or we could use non-linear model ﬁtting of the model to the data:
ke ¼ 0:500 hÀ1: T1=2 ¼ ln2 ¼ 1:386 h:
ke
For the absorption constant, and thus the half-life, we need to use Equation 5.11, where we have already obtained ke. Again we could use model ﬁtting of the equation to the data, or we could employ the ‘method of residuals’.


<!-- ===== Page 164 ===== -->

154

Answers

Writing Eq. 5.11 as: Cp ¼ AeÀket À AeÀkat:
If ka [ ke; then as t ! 1 Cp % AeÀket:

We apply this to the ﬁnal three time points of data: a semi-log plot allows us to calculate A and ke from a slope of −0.500 and intercept of 5.00. Note that we get the same value for ke as above (unsurprisingly) but the intercept value is different because of the bioavailability. Now deﬁne the ‘residual’:
R ¼ AeÀket À Cp:

We have all the information we need to calculate R at every time point and by deﬁnition:
R ¼ AeÀkat:

Thus a semi-log plot of R against time will allow ka to be estimated from the slope. Using the ﬁrst three data points (where the residual will be the largest, since absorption dominates here) gives a slope of −3.03. Hence:
ka ¼ 3:03 hÀ1; T1=2 ¼ ln2 ¼ 0:229 h:
ka
We should check at this point that ka > ke, which it is and sufﬁciently so that the assumption we made above is reasonable.
(c) To calculate the volume of distribution we need the initial plasma concentration. We can use the data we have in part (a), for example using the intercept from the IV administration.
Cp0 ¼ 199:94 mg/L:

Thus

D Vc ¼ 0 ¼ 10:0 L:
Cp


<!-- ===== Page 165 ===== -->

Answers

155

Which is larger than the total plasma volume, so must include some fast exchanging tissue. D
(a) We need Eq. 5.11
CpðtÞ ¼ FD ka ÀeÀket À eÀkatÁ: Vc ka À ke

(b) We can ﬁnd the maximum dose by ﬁrstly ﬁnding the maximum concentration, for which we will need to determine the time of maximum concentration by ﬁnding the turning point of the function described by Cp. This gives
 tmax ¼ 1 ln ka ¼ 21:7 min:
ka À ke ke

Substituting into the expression for Cp and then converting to dose

VcCmax p

Dmax ¼

¼ 1330 mg:

F

It is possible to ﬁnd a nice simpliﬁed form for the maximum concentration with a bit of effort:

max FD kaÀke=ka À ke

Cp ¼

:

Vc ke

(c) The drug is no longer effective once C p< X where X = 20 mg/L, thus we need to solve for the time at which:
CpðtÞ ¼ FD ka ÀeÀket À eÀkatÁ ¼ X: Vc ka À ke
Noting that ke ≪ ka, the absorption process is very rapid in comparison to elimination, so we might assume there is no further absorption by the time that the concentration drops below the level for efﬁcacy. We can thus simplify the expression assuming that the exponential term containing ka is zero:


<!-- ===== Page 166 ===== -->

156

Answers

FD ka eÀket ¼ X: Vc ka À ke

Giving:

1 ka À ke Vc 

t ¼ À ln

X ¼ 606 min:

ke

ka FD

We could check our assumption from above that absorption isn’t important by this time by comparing 606 min to the time constant for absorption (1/ka) which is approximately 5 min.
(d) Michaelis-Menten kinetics are of the form:

VmaxC : C þ Km

This is linear if Km ≫ C, ﬁrst order kinetics, but is constant if Km ≪ C, zeroth order kinetics. In this case Km is an order of magnitude greater than C at any point in time, given that Cp,max is around 100 mg/L. So we would conclude that the analysis still holds as the elimination would still look like ﬁrst order and has not saturated.
6. Tissue mechanics
A
(a) The one-dimensional equations are:
@rx À qg ¼ 0 @x
ex ¼ @u @x
ex ¼ rx E
Hence:
@2u ¼ qg @x2 E
Integrate twice, and substitute in the boundary conditions given to derive the answer.


<!-- ===== Page 167 ===== -->

Answers

157

(b) At the top of the tissue:

u ¼ qgL2 2E

This is approximately 1 mm (10 % of the tissue height) for the values given.

B

(a) Re-arrange and square the result:

3Ke þ cÃ ¼ cÃ2 2 þ RT

w f !2 /0 c0

3

e

þ

/

w 0

Then multiply out the LHS and re-arrange to get the answer given. (b) The result is obviously very non-linear, with concentration becoming
very high at low values of pressure.
C
(a) The one-dimensional equations are:

@2u

G @e @p

G 2þ

¼a

@x 1 À 2m @x @x

e ¼ @u @x

j @2p ¼ a @e þ 1 @p l @x2 @t Q @t

Integrate the ﬁrst equation wrt x:

2Gð1 À mÞ e ¼ p að1 À 2mÞ

Substitute into the last equation: j @2p a2ð1 À 2mÞ 1  @p l @x2 ¼ 2Gð1 À mÞ þ Q @t

Hence the expression given, where the coefﬁcient is: 1 l a2ð1 À 2mÞ 1  c ¼ j 2Gð1 À mÞ þ Q


<!-- ===== Page 168 ===== -->

158

Answers

(b) Easiest way is to take Laplace transforms (with zero initial condition):
@2p À s p ¼ 0 @x2 c
Solve, ignoring the positive exponential term (which would tend to inﬁnity):
p ¼ AeÀ c pﬃsx

Use the boundary condition (Laplace transformed): p ¼ P eÀ c pﬃsx s

This can be inverse Laplace transformed (using a standard result) to give:



 

x

p ¼ P 1 À erf pﬃﬃﬃﬃ

2 ct

D Boundary conditions are:
rrjr¼R ¼ Àp rrjr¼R þ h ¼ Àpext
These are obviously satisﬁed. E
(a) The mean ﬂow velocity is found from:

pR2U ¼ Z u R ðrÞdA

r¼0

2Umax ZR   r n

U¼ 2

1À

rdr

R r¼0

R



U ¼ Umax n

nþ2

(b) The frictional force is given by: 
f ¼ 2pRl@u ¼ À2pnlUmax ¼ À2pðn þ 2ÞlU @r r¼R


<!-- ===== Page 169 ===== -->

Answers

159

7. Cardiovascular system I
A For the numbers given, cardiac output would be 200/(0.21 − 0.16) = 4000 ml_blood/minute. Stroke volume = 4000/60 = 67 ml_blood.
B
(a) The RR interval is 0.8 s, so the heart rate = 60/0.8 = 75 bpm. There is no variability shown here, which is not realistic.
(b) You should ﬁnd that it goes up quite rapidly, the additional cardiac output providing more oxygen to your muscles.
8. Cardiovascular system II
A
Integrate up the equation wrt radius twice:

lu ¼ r2 dp þ A ln r þ B 4 dx

For the solution to be ﬁnite at the origin, A = 0. Also the velocity is zero at the wall, hence:

u ¼ 1 Àr2 À R2Á dp

4l

dx

Flow rate:

q ¼ ZR uðrÞdA ¼ ZR 1 Àr2 À R2Á dp 2prdr ¼ dp pR4

r¼0

r¼0 4l

dx

dx 8l

Since the pressure gradient is the pressure drop divided by the vessel length, we get:

Dpq ¼ pR4 8lL

B
When placed in parallel, the pressure difference is the same for each vessel, with the total ﬂow rate being the sum of the individual ﬂow rates. Hence:

XN q ¼ Dp ¼ D XN p 1 ¼ Dp N

i¼1 R

i¼1 R

R

The overall resistance is thus R=N:


<!-- ===== Page 170 ===== -->

160

Answers

C
(a) It is easiest to work in terms of inﬁnitesimal strains, since compliance is deﬁned as the rate of change of volume with pressure:

dV dA

dR 2pR2L dR 2pR2L

C ¼ ¼ L ¼ 2pRL ¼

¼

deh

dp dp

dp dp R dp

Substitute in Hooke’s law in polar co-ordinates:

2pR2L 1

C¼

ðdrh À mdrr À mdrzÞ

dp E

Substitute in the stress components to give:

C ¼ 2pR3L 1 À m

Eh

2

This gives the quoted result, since Poisson’s ratio is equal to 1/2.
(b) When placed in parallel, capacitors essentially simply become one large capacitor with storage capacity (capacitance) adding. Hence N capacitors have capacitance CN. The same applies for compliance.
D
You should be able to calculate the values easily.
E
(a) Denoting the pressure at entrance to the capillary compartment by Pa, conservation of current/ﬂow at this node gives:

Pin À Pa þ 0 À Pa þ 0 À Pa ¼ 0 Ra þ ixIa Rc þ Rv þ ixIv 1=ixCa

The ﬂow through the capillaries is then:
q ¼ Pa Rc þ Rv þ ixIv
¼ Pin ðRa þ ixIa þ Rc þ Rv þ ixIv þ ixCaðRa þ ixIaÞðRc þ Rv þ ixIvÞÞ

(b) This is of the form of a (third-order) low-pass ﬁlter. This is important because it ﬁlters out the pulsatile nature of the ﬂow in the aorta such that ﬂow is steady by the time that it reaches the capillaries.


<!-- ===== Page 171 ===== -->

Answers

161

F Equation 1.13 shows that inductance can be neglected even in the larger vessels that we are considering here. The transfer function thus simpliﬁes to:
q ¼ Pin ðRa þ Rc þ Rv þ ixCaRaðRc þ RvÞÞ

This has time constant:
s ¼ CaRaðRc þ RvÞ Ra þ Rc þ Rv
Any frequencies above the cut-off frequency set by this time constant will be ﬁltered out, hence we need:
2p [ Ra þ Rc þ Rv CaRaðRc þ RvÞ

G (a) We know that ﬂow is proportional to the product of pressure difference (which will be P here) and radius to the power four:
q ¼ k1PR4

If compliance is constant, then the volume is proportional to pressure: V ¼ k2P
Since volume is proportional to radius squared: P ¼ k3R2
Putting these all together gives: q ¼ k1k3R6
(b) Force balance on the ﬂuid gives wall shear stress as:

sw2pR ¼ dp pR2 dx


<!-- ===== Page 172 ===== -->

162

Answers

Hence: Hence:

sw ¼ dp R dx 2
sw ¼ k4R3

H (a) If the vessel is incompressible, then the cross-sectional area must be the same at all times:
ðR þ hÞ2ÀR2 ¼ ðRo þ hoÞ2ÀRo2

Hence:

qﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ

h ¼ ÀR þ

R2

þ

2Ro

ho

þ

h2
o

(b) Clearly, as R increases, h decreases. Resistance is simply inversely proportional to vessel radius to the power four, so it drops very rapidly with increased radius.
(c) Compliance is proportional to radius to the power three and inversely proportional to wall thickness, so as radius increases, compliance also goes up very rapidly.
9. The Respiratory System
A
In the steady state with no generation or consumption of the gas involved the diffusion equation for the partial pressure of gas in the membrane is:
@2c D 2 ¼ 0:
@x
The boundary conditions are:
• Concentration of the gas on the airspace side of the membrane (x=0). For this we need to use the Ostwald co-efﬁcient to ‘convert’ partial pressure of gas into a concentration: cðx ¼ 0Þ ¼ rpg:
• Concentration of gas in the blood: cðx ¼ LÞ ¼ cb. Solving and using Fick’s law the ﬂux is thus:
q ¼ D Àcb À rpgÁ: L
We can deﬁne D/L as the surface diffusion co-efﬁcient Ds, which is a property of the membrane.


<!-- ===== Page 173 ===== -->

Answers

163

B
(a) Àf dx dCðxÞ ¼ 2prDsðCðxÞ À CoÞ (b) The equation is a ﬁrst order differential equation, so can be written in the
form:

f dC þ C ¼ Co 2prDs dx

which has the solution (given the boundary condition):





C ¼ Co þ ðCin À CoÞexp À 2prDsx

f

(c) The ﬂux is found by integrating the function above

ZL Q ¼ 2prDsðCðxÞ À CoÞdx
x¼0

to give:



!

Q ¼ ðCin À CoÞf 1 À exp À 2prDsL

f

(d) The ﬂux is 4e−14 mM/s for baseline ﬂow, 3.2e−14 mM/s and 4.5e −14 mM/s for halved and doubled ﬂow. Hence it is relatively constant with ﬂow rate in this region (ﬂux saturates at high ﬂows, increasing proportionally less than ﬂow).
(e) Two competing effects: increasing the ﬂow increases the oxygen ﬂux into the capillary, but it passes through the vessel more quickly, so has less chance to diffuse into the surrounding tissue.
(f) This gives Eq. 10.4, the equation no longer depends upon the diffusion properties of the capillary wall only on perfusion and concentration (partial pressure) differences. A large surface area for gas transfer is present in the lungs and the membrane is thin, thus diffusion doesn’t limit the overall transfer of gas, thus L is large compared to the diffusion ‘distances’ involved.
C
(a) Using reaction kinetic principles from Chap. 1, the equilibrium constant for the second part of the reaction scheme is given by:


<!-- ===== Page 174 ===== -->

164

Answers

ÂHCO3ÀÃ½H þ  KA ¼ ½H2CO3 :

(b) If almost all the available Co2 converts to carbonic acid, then the con-

centration of CO2 is very similar to that of H2CO3, thus the ‘corrected’

equilibrium constant is:

ÂHCO3ÀÃ½H þ  KA ¼ ½CO2 :

D (a) In Exercise B the governing equation for gas concentration in the capillary blood was:
Àf dCðxÞ ¼ 2prDsðCðxÞ À CoÞ dx

This can be applied to CO2, but we now need to account for the conversion to bicarbonate. As suggested model this using a simpliﬁed reaction scheme that ignores the intermediary H2CO3:
K1 À þ
CO2 þ H2O  HCO3 þ H
kÀ1
Including the ‘loss’ of CO2 to bicarbonate and the reverse process where bicarbonate converts back to CO2:
f dC ¼ 2prDsðrCO2 PCO2 À CÞ þ kÀ1½H þ D À k1C; dx
where we use D to signify [HCO3-] as we have used C to represent [CO2]. We also have an equation for D, but as this exists only in solution we do not have to worry about the gas exchange part only the reaction kinetics:
f dD ¼ k1C À kÀ1½H þ D: dx

(b) Combining the two equations gives: f d ðC þ DÞ ¼ 2prDsðrCO2 PCO2 À CÞ: dx


<!-- ===== Page 175 ===== -->

Answers

165

(c) Taking a quasi-steady state approximation allows us to write D ¼ KaC where Kc ¼ k1=ðkÀ1½H þ Þ: Thus, if [H+] is constant with respect to x:
f ð1 þ KcÞ dC ¼ 2prDsðrCO2 PCO2 À CÞ: dx
This is practically identical to the result in Exercise B and thus the solution for ﬂux in the limit will be the same except for an ‘ampliﬁcation’ of (1+Kc), hence Eq. 9.6. (d) We can ﬁnd the relationship between Kc and Ka using the result in Exercise C:
Ka ¼ Kc½H þ 

Since log10Ka = −6.1 and pH=-log10[H+] = 7.4 typically, Kc is around 20. A substantial ampliﬁcation of the ﬂux of CO2 allowing more rapid removal from the body than would be achievable by having CO2 alone in solution. E
(a) This is a matter of taking logs of the expression from Exercise C part b) and re-arranging in terms of -log10[H+] i.e. pH.
(b) For the values given, [CO2] = 1.2 mM and pH = 7.4. (c) This is called the Davenport diagram and is shown below. Large changes
in pH can be gained by adjusting both pCO2 and bicarbonate concentration, so the lungs and kidneys have a lot of control over pH.

(d) The kidneys need to excrete H+ and reabsorb HCO3- to balance pH again. This would happen in a person with poor respiration (not enough removal of CO2 from the lungs).


<!-- ===== Page 176 ===== -->

Further Reading
Cardiovascular Physiology (8th edition): Mohrman, Heller. McGraw-Hill, 2013. Cellular Physiology of Nerve and Muscle (4th edition): Matthews. Blackwell, 2002. Mathematical Physiology (2nd edition): Keener, Sneyd. Springer, 2008. Molecular Biology of the Cell (6th edition): Alberts, Johnson, Lewis, Morgan, Raff, Roberts and
Walter. Garland Science, 2014. The Cardiovascular System at a Glance (4th edition): Aaronson, Ward and Connolly.
Wiley-Blackwell, 2012. The Respiratory System at a Glance (3rd edition): Ward, Ward and Leach. Wiley-Blackwell, 2010. Tissue Mechanics: Cotwin, Doty. Springer, 2007.

© Springer International Publishing Switzerland 2016

167

M. Chappell and S. Payne, Physiology for Engineers,

Biosystems & Biorobotics 13, DOI 10.1007/978-3-319-26197-3
