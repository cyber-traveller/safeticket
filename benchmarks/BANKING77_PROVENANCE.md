# BANKING77 external benchmark provenance

Source: [PolyAI task-specific datasets](https://github.com/PolyAI-LDN/task-specific-datasets),
official `banking_data/test.csv` and category list.

The BANKING77 dataset is distributed under Creative Commons Attribution 4.0
International (CC BY 4.0). The downloaded files are stored under
`work/external/banking77/` for local evaluation only. Any redistribution must
preserve the dataset attribution and license terms.

The external test split contains 77 fine-grained banking intents. SafeTicket exposes
five coarse support teams, so `benchmarks/build_banking77_external.py` maps
each source intent to a coarse team. That mapping is an evaluation assumption,
not an official BANKING77 label. Consequently, the 77-case result is a domain
coverage diagnostic and must not be used as a direct model leaderboard.
