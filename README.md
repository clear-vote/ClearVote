# Statements
Politicians use data to profile you, so this app uses data to profile politicians.
Everyone deserves to know who they are voting for!
# Goal
Get people voting *more* for the [[off-cycle elections]] than [[federal elections]]
## Why
- Authoritarian rulership prevents humanity from seeking truth and aspiring to higher ideals. These ideals can enable innovation driven by a higher purpose, as opposed to those driven by nationalism or capital. With enough of these ideals, we can shape society’s collective intent to one that strives to provide all life, present and future, with the means to achieve its full potential. 
- Enhancing the political agency of individuals is the best way to prevent Authoritarianism from taking control in human societies. Democracy does give people the means to exert this political agency, but it’s most effective at a smaller scale where:
	- constituents are more likely to interact with their representatives
	- representatives are more likely to consider their constituent’s needs
	- and faster, more effective action can be taken in a way that best fits the needs of the community
- If people were to participate in [[off-cycle elections]], more than the [[federal elections]], we would see a revolutionary shift in power that enables communities to be more adaptable and engaged. On an individual level, this would grant personal agency to the individual need to prevent authoritarianism from taking root in society, enabling more well-intentioned innovations driven by higher ideals

## How
Estimates for voter turnout in [[federal elections]] are around 70% with [[off-cycle elections]] in contests like [[primary election]]s being as low as 20%. Many people *are* interested in participating but do not, mainly because they either:
1. They do not even know there is an election going on
2. They don’t have the time to figure out how to participate
3. They are not able to keep track of the key dates and miss their schedule
4. Even worse, ballots themselves tend to be vague and require busy would-be voters to read complicated voter pamphlets read between the lines from biased articles and news sources to figure out what the people they are voting for really represent. Those who don’t opt out entirely are prone to vote for a person purely on the basis of their political party and not the values they actually represent
We aim to create a service that makes staying *up-to-date* and *informed* on off-cycle elections easy with clear instructions and alerts that tell them exactly *what to do* and most importantly: ***what the values are of the candidates on their ballot***

## What
>Find information quickly and reliably, to the expense of accuracy if unable to do so

# Challenges
1. ~~Creating a [[composite zone]] (not yet applicable)~~
2. Finding the districts, given a [[composite zone]] (address).
	- There are 50 states. Finding state and US legislative representation is quite easy, but the local stuff is very difficult with this data
	- There are 3,034 counties which are mutually exclusive and span the entire country
		- This usually tells more about at least the major towns and municipalities, and this is likely the best place to start when looking for district resources in combination with GIS tools if possible
	- There are 41,704 zip codes. Zip codes don’t have elections, but they do span the entire country, making them a straightforward way of zoning addresses into blocks
	- There are 13,506 school districts which are mutually exclusive and span the entire country with their own systems of government in place
	- There are 19,429 municipalities and 16,504 townships. Neither spans the entire US, (the rest of it is covered by unincorporated areas, federal land, state land, and native reservations), but these communities do have their own systems of government in place
3. [[The watcher/updater]] Catching all the updates (upcoming elections, election openings, register-by dates, closing times, and results postings)
	- voter pamphlet
	- ballot updates
	- scraping directly from the websites
4. [[The mapper]] Creating internal mappings from:
	- GIS tools
	- Coordinate sets
	- JPEG-form maps posted on the website
5. [[The judge]] Look up and analyze sentiments of candidates in a given zone
	- ChatGPT
		- Model off [ski-gpt](https://github.com/EliasBelz/ski-gpt) and Elias’s [powerpoint](https://docs.google.com/presentation/d/1WC_2opcSBKXVTBn3wCuD4wJ4v-luWxzCnf1rEABKvPY/edit#slide=id.p)
		- Find inputs (search {firstname} {lastname} {jurisdiciton name}) and return lots of text data
			- [voter pamphlets](https://kingcounty.gov/~/media/depts/elections/how-to-vote/voters-pamphlet/2023/08/edition-1.ashx?la=en)
			- personal websites
			- news articles
		- Compile all the data and run {sentiments} with appropriate [[political value metrics]]
	- Compile sentiments (0-100) for each candidate, subtracting the minimum sentiment in the dataset
6. Recognize when redistricting occurs and adapt accordingly (not yet applicable)
# 1.0 (Back end)
## Page 3 (Candidate portal)
- [x] Hardcode an address [[composite zone]]s with appropriate candidate info
	- see [[Finding candidate info]]
- [x] Determine the [[political value metrics]] that will be used in sentiment analysis for the following jurisdictions on the August ballot
- [x] Create a means of compiling web data into [[prompts for ChatGPT]] on candidates and analyzing political sentiments. Also include relevant [timestamps](https://www.epochconverter.com/) for the election. This can be hardcoded for now
	- see [[The judge]]
- [x] For each candidate, have it calculate their top *unique* political stances and *record how this calculation is performed*
# 1.1
## Page 2 (Dates and Registration)
1. For now, just put “The next election in your area opens up on xx/xx and closes at xx/xx by X:XXpm”
	- [[Ballots]]
2. Option to continue on to the next page
## Page 1 (Finding the user’s jurisdiction)
1. Enable user to select zip code from a dropdown
2. (Make it catered towards Seattle!)
3. (Why do you need this? ~ Clearvote is a non-profit service intended to help foster stronger local communities and more informed voters. We will *never* collect any more information from you then we need to help you do that!)
4. Option to continue on to the next page
## Page 4 (Collecting the user’s info)
1. Show a map with ballot boxes in the area of the zip code. *Record how this is done*
2. (Mention something about how mail in voting works)
3. Ask the user to enter their name, and either their sms line or email
4. Send a text or email outlining their ballot information on submission and move on to the next page
## Page 5 (Recruitment)
1. We need YOU to help Clearvote grow! ~ Clearvote is a student run, non-profit organization. If this is something you would like to see in the world, email jkru3@cs.washington.edu for more information or call 360-763-3490
2. Back to the first page

There are on-cycle and [[off-cycle elections]]

1. Federal jurisdiction (presidential)
2. [[State]] jurisdiction (Governor, Senator)
3. ~~Territories~~
4. [[County]] Jurisdiction (???) 
5. [[Municipality]], like cities, towns and incorporated communities (Mayor, City Council)
- Congressional Districts (US House of Representatives)
7. State Senate (State Senate)
8. State House/Assembly districts (State House of Representatives)
9. Judicial Districts (???)
10. School Districts (???)
11. Fire Districts
12. Water Districts
13. Sewer Districts
14. Public Utility Districts
15. Transit Authorities
16. Library Districts
17. Parks and Rec Districts
18. Hospital/Health Districts
19. Flood Control/Drainage Districts
20. Sanitation Districts
21. Conservation Districts
22. Mosquito Abatement Districts
23. Community College Districts
24. Air Quality/Air Pollution districts
25. **Cemetery Districts**
26. **Ambulance or Emergency Medical Service Districts**
27. **Port Authorities or Port Districts**
28. **Housing Authorities**
29. **Development or Redevelopment Districts**
30. **Tourism or Visitor Districts**
31. **Business Improvement Districts (BID)**
32. **Levee or Dike Districts**
33. **Lighting Districts**
34. **Weed Control Districts**
35. **Animal Control Districts**
36. **Native American Reservations/Tribal Jurisdictions**
37. **Other Special Jurisdictions**

# 2.0 (Front end)
# Resources
## Websites
https://www.usvotefoundation.org/
https://civicdata.usvotefoundation.org/
https://info.kingcounty.gov/kcelections/Vote/contests/ballotmeasures.aspx?eid=38
https://gis-kingcounty.opendata.arcgis.com/
https://www.vote.org/

## Zip Codes
Every zip code is associated with a “central“ address. That address is the point on at the center of the zip
City/County (for rural areas) + State + Zip geocached address

Zip codes
98101
98102
98103
98104
98105
98106
98107
98108
98109
98112
98115
98116
98117
98118
98119
98121
98122
98125
98126
98133
98134
98136
98144
98146
98154
98164
98174
98177
98178
98195
98199