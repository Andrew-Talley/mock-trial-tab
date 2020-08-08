# mock-trial-tab

## Getting set-up
### Starting Server
1. Run `source py-env/bin/activate`
2. Run `npm run start-server` (or `python3 -m gql_server.gql`)

The server will then be available on localhost:5000/graphql

## Testing
### Python
1. Run `source py-env/bin/activate`
2. Run `npm run test`

## Contributing
If you want to contribute, thank you! You can help whether or not you know python, or know how to code at all.

### How anyone can contribute:
1. Test all of it! Go through, make a new tournament, sign up friends as judges, submit ballots, add teams, and give yourself the individual awards you know you deserve. If it doesn't work, file a bug 🐞 [on GitHub](https://example.com), or email it to email@email.com
2. Test the round pairings! We can never be too certain that the code for generating pairings truly works. To do this, find an AMTA-sanctioned tournament that is not a 2020 ORCS tournament (because of the new pairings system). Then, choose a round in the tournament. Don't choose R1, nor R4 of a regional or ORCS tournament, since those are paired differently. Then, create a google sheets, and for each team, place the following information in each column:
   - Their team number (and name, if you want to)
   - The name of the school (make sure this **exactly** matches every other team from that school)
   - The number of wins, losses, and ties up until the round you chose
   - Their PD up until that round
   - (If it is R3 or R4) Their CS up until that round
   - (If it is R4) Their OCS up until that round
   - Each team they faced, separated by commas
3. Feature requests! Want to take credit for some cool new feature without doing any work? Then feature requests are for you! If there's something that you think would help, either open a new issue [on GitHub](https://example.com), or email it to email@email.com

### How developers can contribute:
1. Add tests!
2. Improve performance
3. Address any open bugs, or ask to take on a feature request (if you want to add your own feature, open an issue first to get the go-ahead).