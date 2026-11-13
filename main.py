from drafter import *
from dataclasses import dataclass
from bakery import assert_equal

set_website_title("Bitcoin Mining Decentralization Analyzer")
set_site_information(
    author="Jemuel Picol",
    description="Explore how bitcoin mining is distributed among mining pools and analyze mining concentration.",
    sources="Thanks to the Drafter docs and my study group.",
    planning=["CS1 Final Project 0 Pick a problem", "CS1 Final Project 1 Design"],
    links=[
           "https://github.com/jem-uel/bitcoin-mining-decentralization-analyzer/blob/main/CS1%20Final%20Project%200_%20Pick%20a%20Problem.pdf",
           "https://github.com/jem-uel/bitcoin-mining-decentralization-analyzer/blob/main/CS1%20Final%20Project%201_%20Design.pdf"
           ]
)

hide_debug_information()
set_website_framed(False)

@dataclass
class MiningPool:
    """
    Store a mining pool's name, block count, observation period, and share.
    """
    name: str
    blocks_mined: int
    period: str
    share: float

@dataclass
class State:
    """
    Store the user's settings, mining pool data, and analysis results.
    """
    top_count: int
    threshold: float
    pools: list[MiningPool]
    selected_pool:str
    combined_share:float
    

def calculate_total_blocks(pools: list[MiningPool]) -> int:
    """
    Calculates the total number of blocks in the mining pool dataset.
    """
    total = 0

    for pool in pools:
        total = total + pool.blocks_mined
    return total

def calculate_pool_shares(pools: list[MiningPool]) -> None:
    """
    Calculate each mining pool's percentage of the total observed blocks.
    """
    total_blocks = calculate_total_blocks(pools)

    for pool in pools:
        if total_blocks > 0:
            pool.share = (pool.blocks_mined / total_blocks) * 100
        else:
            pool.share = 0.0
            
def calculate_combined_share(pools: list[MiningPool],
                             top_count:int) -> float:
    """
    Calculate the combined percentage of the selected largest mining pools.
    """
    combined = 0.0
    for pool in pools[:top_count]:
        combined = combined + pool.share
    return combined

def rank_pools(pools: list[MiningPool]) -> list[MiningPool]:
    """
    Sort mining pools from most blocks mined to fewest blocks mined.
    """
    ranked = sorted(pools, key=lambda pool: pool.blocks_mined, reverse=True)
    return ranked


def validate_inputs(top_count: int, threshold: float, pools: list[MiningPool]) -> str:
    """
    Check user inputs and return an error message if any values are invalid.
    """
    if top_count < 1:
        return "Error: You must select at least one mining pool."

    if top_count > len(pools):
        return "Error: You selected more mining pools than are available."

    if threshold < 0 or threshold > 100:
        return "Error: Threshold must be between 0 and 100."

    return ""
            
@route
def index(state: State) -> Page:
    """
    Display the homepage with a description and navigation buttons.
    """
    return Page(state, [
        "Bitcoin Mining Decentralization Analyzer\n",
        "Explore how bitcoin mining is distributed among mining pools and analyze mining concentration.",
        Button("Start Analysis", "configure"),
        Link("About This Analyzer", "about"),
    ])



@route
def configure(state: State, selected_pool: str = "") -> Page:
    """
    Display input fields for the number of pools and concentration threshold.
    """
    return Page(state,[
        "Configure your Analysis",
        "Numer of largest mining pools (1 to" + str(len(state.pools)) + "):",
        TextBox("top_count", state.top_count),
        "Concentration threshold (%):",
        TextBox("threshold", state.threshold),
        Button("Run Analysis", "analyze"),
        Button("Reset Settings", "reset_settings"),
        Link("Return Home", "return_home"),
    ])

@route
def analyze(state:State, top_count:int, threshold:float)->Page:
    """
    Validate inputs, calculate mining shares, rank pools, and display results.
    """
    error = validate_inputs(top_count, threshold, state.pools)
    if error != "":
        return Page(state, [
            "Invalid analysis settings: " + error,
            Button("Try Again", "configure"),
        ])

    state.top_count = top_count
    state.threshold = threshold
    calculate_pool_shares(state.pools)
    state.pools = rank_pools(state.pools)
    state.combined_share = calculate_combined_share(state.pools, state.top_count)
    return results(state)

@route
def results(state:State)-> Page:
    """
    Display mining pool rankings, combined share, and concentration analysis.
    """
    rows = []
    pool_names = []
    rank = 1
    for pool in state.pools:
        rows.append([rank, pool.name, pool.blocks_mined, str(round(pool.share, 2)) + "%"])
        pool_names.append(pool.name)
        rank = rank + 1

    if state.combined_share > state.threshold:
        conclusion = "The selected pools' combined share exceeds your threshold."
    elif state.combined_share == state.threshold:
        conclusion = "The combined share is exactly equal to your threshold."
    else:
        conclusion = "The selected pools' combined share is below your threshold."

    return Page(state, [
        "Bitcoin Mining Analysis Results",
        "Total observed blocks: " + str(calculate_total_blocks(state.pools)),
        "Top pools selected: " + str(state.top_count),
        "Threshold: " + str(state.threshold) + "%",
        "Combined share: " + str(round(state.combined_share, 2)) + "%",
        conclusion,
        "Mining Pool Rankings",
        Table(rows, ["Rank", "Pool", "Blocks Mined", "Share"]),
        "Select a mining pool to inspect:",
        SelectBox("selected_pool", pool_names, state.selected_pool),
        Button("View Pool Details", "choose_pool"),
        Button("Change Settings", "configure"),
        Link("About This Analyzer", "about"),
    ])

@route
def choose_pool(state: State, selected_pool: str) -> Page:
    """
    Save the user's selected mining pool and open its details page.
    """
    state.selected_pool = selected_pool
    return pool_details(state)

@route
def pool_details(state: State) -> Page:
    """
    Display the selected pool's name, blocks mined, period, and percentage share.
    """
    for pool in state.pools:
        if pool.name == state.selected_pool:
            return Page(state, [
                "Mining Pool Details",
                "Pool name: " + pool.name,
                "Blocks mined: " + str(pool.blocks_mined),
                "Observation period: " + pool.period,
                "Share of observed blocks: " + str(round(pool.share, 2)) + "%",
                Button("Back to Results", "results"),
            ])

    return Page(state, [
        "The selected mining pool was not found.",
        Button("Back to Results", "results"),
    ])

@route
def about(state: State, selected_pool: str = "") -> Page:
    """
    Explain the website's purpose, calculations, and data limitations.
    """
    return Page(state, [
        "About This Analyzer",
        "Purpose: This website helps visitors explore how observed Bitcoin blocks are distributed among mining pools.",
        "How pool shares are calculated: Divide a pool's block count by the total blocks in the sample, then multiply by 100.",
        "How combined share is calculated: Rank pools by blocks mined and add the shares of the largest number of pools chosen by the user.",
        "Threshold comparison: The site compares this combined percentage with the visitor's selected threshold.",
        "Limitations: The current block counts are fictional sample data, not live Bitcoin statistics. Mining pool concentration alone cannot prove coordinated control of the Bitcoin network.",
        Button("Back to Results", "results"),
        Link("Return Home", "index"),
    ])

@route
def return_home(state:State, top_count:int, threshold:float)->Page:
    """
    Return the user to the homepage from the configuration page.
    """
    return index(state)

@route
def reset_settings(state: State, top_count: int, threshold: float) -> Page:
    """
    Restore the default analysis settings and return to configuration.
    """
    state.top_count = 3
    state.threshold = 50.0
    state.selected_pool = "Pool A"
    state.combined_share = 0.0

    return configure(state)

assert_equal(
    calculate_total_blocks([
        MiningPool("Test A", 10, "Test", 0.0),
        MiningPool("Test B", 20, "Test", 0.0)
    ]),
    30
)

start_server(State(3,50.0, [
    MiningPool("Pool A", 120, "Sample Week", 0.0),
    MiningPool("Foundry USA", 100, "Sample Week", 0.0),
    MiningPool("AntPool", 90, "Sample Week", 0.0),
    MiningPool("F2Pool", 75, "Sample Week", 0.0),
    MiningPool("ViaBTC", 65, "Sample Week", 0.0),
    MiningPool("SpiderPool", 50, "Sample Week", 0.0),
    ],"Pool A", 0.0))


