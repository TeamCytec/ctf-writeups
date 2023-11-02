# Challenge 10 - FrontStonks
- Solved by: @Elma, @BaeSenseii
- Flag: hli{i_ExpECT_TO_BEcome_4_CaPYLl1onN4IrE}

## Screenshot of Challenge
![alt](./images/chall-screenshot.png)

## Writeup
This is proably gonna be a short write-up because it is really TOO easy as it just involves just a simple task of registering for an account.

![](./images/actf2023_c10_1.PNG)

![](./images/actf2023_c10_2.PNG)

Under the “How much are you planning to earn on stocks?” portion of the registration, it does not allow values above 0. And if we put 0, we cannot proceed with the registration.

![](./images/actf2023_c10_3.PNG)

![](./images/actf2023_c10_4.PNG)

However, there was no HTTP request being sent to the server when entering the value, so we can assume that there's some form of client-side input validation in place. If we look closely at the input field using the Browser Debugger tool, the field is set to the configuration of 'max="0", in which we can easily remove it:

![](./images/actf2023_c10_5.PNG)

Once removed you can proceed to key in ANY value:

![](./images/actf2023_c10_6.PNG)

Once done, log into the system with your new account and go to your Profile > Claims to get your flag (it was blurred out, but you can just click on it to see your flag.)

![](./images/actf2023_c10_7.PNG)