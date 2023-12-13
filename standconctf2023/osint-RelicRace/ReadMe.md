# OSINT - Relic Race
- Solved by: DocileMango
- Flag: STANDCONE{N4 2AW}

## Writeup
Note: The flag will be in STANDCONP{} format with a postal code as the answer

Looking at the image that was given:

![](./images/relic-race_0.png)

If we read the email seen in the image, it can tell us a few things:

![](./images/relic-race_1.png)

- We are sent an airticket
- There is an image of 2 landmarks, gas station and bank(target location)

Let's look at the barcode that we can see in the image:

![](./images/relic-race_2.png)

Using pageloot.com/barcode-scanner/, we can see what is inside, and we get the following:

![](./images/relic-race_3.png)

From what we got, we can assume that this is the airticket mentioned in the email.
With this, we can make some assumptions about the location.

"SINLHRBN" basically represents Singapore(SIN) to London Heathrow(LHR). From this information we can guess that the image could likely be in London, United Kingdom.

Let's look at photo provided in the image:

![](./images/relic-race_4.png)

From the assumption that this image could be in London, I searched up on Google Images "big stone in london"

After doing this search, I find a rock that looks similar to the glitched rock image:

![](./images/relic-race_5.png)

We then visit this page:

![](./images/relic-race_6.png)

From here, we found out that this rock is known at the "London Stone" and that it is located at Cannon Steet in London.

But before that, we searched up what the London Stone and we found this on Google Images:

![](./images/relic-race_7.png)

Looks familiar? We have found the photo of the glitched out rock, and we have confirmed that this rock is in Cannon Street at London.

Let's now turn to google maps and look for the location:

![](./images/relic-race_8.png)

Here we are canonnt street, first look, no much greeneryn as opposed to the image of the location. Let's zoom out and filter out gas stations in london by searching "gas stations london":

![](./images/relic-race_9.png)

I zoomed out a bit to see the whole of london and search for gas stations. If you noticed, there are a lot of gas stations to search for. One thing about searching "gas stations london" is tht it won't show all gas stations in london. So to make our search be easier, we will be filtering by brands.

![](./images/relic-race_10.png)

I have filtered out all shell gas stations in london, now is just looking for the gas station landmark to find our location. To narrow our search even more, I will only be looking at gas stations near greenery as the image shown in the email, the gas station were near some trees and grass:

![](./images/relic-race_11.png)

Once you do some searching, you will realize that shell gas stations are not it, so let's try Texaco

![](./images/relic-race_12.png)

If you noticed, there is a gas station here:

![](./images/relic-race_13.png)

Let's give it a look!

This is what we found:

![](./images/relic-race_14.png)

Looks familiar? We have found the location in the photo!

Now, we check the postal code of the bank, we get our flag!

![](./images/relic-race_15.png)

So our flag would be: STANDCON{N4 2AW}