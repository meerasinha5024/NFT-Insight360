from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ContextTypes
from collection_score import get_collection_score
from wallet_profile import get_wallet_profile
from price_prediction import get_price_prediction
from analytics import fetch_analytics,plot_and_send_analytics
from collection_holders import fetch_holder_data,plot_holder_trend
from collection_metadata import search_nft
from trader_trend import display_trader_trend
from collection_washtrade import display_washtrade_trends
import market_price_trend
from config import TELEGRAM_TOKEN
import aiohttp

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # Get the user object
    user_id = user.id             # Access user ID
    await update.message.reply_text(
        f"Hello {user.first_name}, your Telegram user ID is {user_id}. Welcome to NFT Insight 360!. Let start by putting your wallet address."
    )

async def display_options(update_or_message, context: CallbackContext, clear_nft=False):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    
    if clear_nft:
        context.chat_data.pop('nft_contract_address', None)

    if 'wallet_address' not in context.chat_data:
        wallet_address = message.text
        context.chat_data['wallet_address'] = wallet_address

    keyboard = [
        [InlineKeyboardButton("Show Wallet Profile", callback_data="profile")],
        [InlineKeyboardButton("Search for NFTs", callback_data="ask_for_contract")],
        [InlineKeyboardButton("Exit", callback_data="exit")] 
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Choose an option:', reply_markup=reply_markup)

    

async def nft_details_menu(update_or_message, context: CallbackContext):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message 
    else:
        message = update_or_message

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Show Collection Metadata", callback_data="show_metadata")],
        [InlineKeyboardButton("Show Collection Score", callback_data="show_score")],
        [InlineKeyboardButton("Show Predicted Price", callback_data="show_price")],
        [InlineKeyboardButton("Check Anomaly", callback_data="check_anomaly")],
        [InlineKeyboardButton("Show Analytics", callback_data="show_analytics")],
        [InlineKeyboardButton("Show Holder Trend", callback_data="collection_holder")],
        [InlineKeyboardButton("MarketCap & Price Ceiling Trend", callback_data="mpc")],
        [InlineKeyboardButton("Trader Trend", callback_data="trader_trend")],
        [InlineKeyboardButton("Washtrader Trend", callback_data="show_washtrade_options")],
        [InlineKeyboardButton("Go Back", callback_data="go_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ensure callback_query exists and use it to edit the message
    
    await context.bot.send_message(chat_id=chat_id, text='What would you like to do next?', reply_markup=reply_markup)

async def show_trend_options(update_or_message, context: CallbackContext):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Last 24 Hours", callback_data="trend_24h")],
        [InlineKeyboardButton("Last 7 Days", callback_data="trend_7d")],
        [InlineKeyboardButton("Last 30 Days", callback_data="trend_30d")],
        [InlineKeyboardButton("All Time", callback_data="trend_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Select the time range', reply_markup=reply_markup)

async def show_specific_trader_trend_menu(update_or_message, context: CallbackContext, time_range):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Buyers Trend", callback_data=f"traders_buyers_trend_{time_range}")],
        [InlineKeyboardButton("Ratio Trend", callback_data=f"traders_ratio_trend_{time_range}")],
        [InlineKeyboardButton("Sellers Trend", callback_data=f"traders_sellers_trend_{time_range}")],
        [InlineKeyboardButton("Overall Trend", callback_data=f"traders_trend_{time_range}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Choose which trend to display:', reply_markup=reply_markup)

async def show_trader_trend_menu(update_or_message, context: CallbackContext):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("24 Hours", callback_data="trader_trend_24h")],
        [InlineKeyboardButton("7 Days", callback_data="trader_trend_7d")],
        [InlineKeyboardButton("30 Days", callback_data="trader_trend_30d")],
        [InlineKeyboardButton("All Time", callback_data="trader_trend_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Select the time range for trader trends:', reply_markup=reply_markup)

async def show_analytics_menu(update_or_message, context: CallbackContext):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Last 24 Hours", callback_data="analytics_24h")],
        [InlineKeyboardButton("Last 7 Days", callback_data="analytics_7d")],
        [InlineKeyboardButton("All Time", callback_data="analytics_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Select the time range for analytics:', reply_markup=reply_markup)


async def show_washtrade_trend_options(update_or_message, context: CallbackContext):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Washtrade Assets Trend", callback_data="washtrade_assets_trend")],
        [InlineKeyboardButton("Washtrade Suspect Sales Trend", callback_data="washtrade_suspect_sales_trend")],
        [InlineKeyboardButton("Washtrade Volume Trend", callback_data="washtrade_volume_trend")],
        [InlineKeyboardButton("Washtrade Wallets Trend", callback_data="washtrade_wallets_trend")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Choose a washtrade trend to display:', reply_markup=reply_markup)

async def show_washtrade_time_range_options(update_or_message, context: CallbackContext, trend_type: str):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Last 24 Hours", callback_data=f"{trend_type}_24h")],
        [InlineKeyboardButton("Last 7 Days", callback_data=f"{trend_type}_7d")],
        [InlineKeyboardButton("Last 30 Days", callback_data=f"{trend_type}_30d")],
        [InlineKeyboardButton("All Time", callback_data=f"{trend_type}_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Select the time range:', reply_markup=reply_markup)

# Anomaly Detection API

async def fetch_anomaly_prediction(features):
    url = "https://nft-nexus-g7co.onrender.com/anomaly-predict"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=features, headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {'prediction': 'Error with the prediction service'}
        except Exception as e:
            return {'prediction': f'An error occurred: {str(e)}'}

# Display Analytics Graph

async def fetch_and_display_analytics(update: Update, context: CallbackContext, time_range: str):
    contract_address = context.chat_data.get('nft_contract_address')
    if not contract_address:
        await update.callback_query.message.reply_text("No contract address found. Please set this first.")
        return

    analytics_data = await fetch_analytics(contract_address, time_range)
    
    if analytics_data:
        await plot_and_send_analytics(analytics_data, update.callback_query.message)
        await nft_details_menu(update.callback_query.message, context)
    else:
        await update.callback_query.message.reply_text("Failed to retrieve analytics data.")

    # Handle query

async def handle_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data == "exit":
        await context.bot.send_message(chat_id=chat_id, text="Thank you for using our service. Feel free to return anytime!")
        context.chat_data.clear()

    elif data == "profile":
        wallet_address = context.chat_data.get('wallet_address')
        print(wallet_address)
        if wallet_address:
            profile = get_wallet_profile(wallet_address)
            if profile and 'data' in profile and profile['data']:
                profile_data = profile['data'][0]
                nft_count = profile_data.get('nft_count', 'N/A')
                washtrade_nft_count = profile_data.get('washtrade_nft_count', 'N/A')
                marketplace_rewards = profile_data.get('nft_marketplace_reward', {})
                blur_rewards = marketplace_rewards.get('blur', 'N/A')
                looks_rewards = marketplace_rewards.get('looks', 'N/A')
                rari_rewards = marketplace_rewards.get('rari', 'N/A')

                message = (
                    f"NFT Count: {nft_count}\n"
                    f"Washtrade NFT Count: {washtrade_nft_count}\n"
                    "Marketplace Rewards:\n"
                    f" - Blur: {blur_rewards}\n"
                    f" - Looks: {looks_rewards}\n"
                    f" - Rari: {rari_rewards}"
                )
            else:
                message = "Failed to retrieve wallet profile or no data available."
        else:
            message = "Please send your wallet address first."
        await context.bot.send_message(chat_id=chat_id, text=message)
        await display_options(update.callback_query.message, context)
    elif data == "ask_for_contract":
        await query.message.reply_text("Please send the contract address for the NFT collection.")
        context.chat_data['action'] = 'awaiting_contract'

    # Show Collection Metadata

    elif data == "show_metadata":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            nft_info = search_nft(contract_address)
            if nft_info and 'data' in nft_info and nft_info['data']:
                nft_data = nft_info['data'][0]
                collection_name = nft_data.get('collection', 'N/A')
                description = nft_data.get('description', 'No description available.')
                image_url = nft_data.get('image_url', 'No image available.')
                discord_url = nft_data.get('discord_url', 'No Discord URL available.')
                external_url = nft_data.get('external_url', 'No website URL available.')
                instagram_url = nft_data.get('instagram_url', 'No Instagram URL available.')
                marketplace_url = nft_data.get('marketplace_url', 'No marketplace URL available.')
                medium_url = nft_data.get('medium_url', 'No Medium URL available.')
                twitter_url = nft_data.get('twitter_url', 'No Twitter URL available.')

                message = (
                    f"Collection Name: {collection_name}\n"
                    f"Description: {description}\n"
                    f"Image URL: {image_url}\n"
                    "Links:\n"
                    f" - Website: {external_url}\n"
                    f" - Marketplace: {marketplace_url}\n"
                    f" - Instagram: {instagram_url}\n"
                    f" - Discord: {discord_url}\n"
                    f" - Twitter: {twitter_url}\n"
                    f" - Medium: {medium_url}"
                )
            else:
                message = "Failed to retrieve NFT data or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."
        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)

    # Show Collection Score

    elif data == "show_score":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            score_data = get_collection_score(contract_address)
            if score_data and 'data' in score_data and score_data['data']:
                collection_data = score_data['data'][0]
                collection_score = collection_data.get('collection_score', 'N/A')
                fear_and_greed_index = collection_data.get('fear_and_greed_index', 'N/A')
                market_dominance_score = collection_data.get('market_dominance_score', 'N/A')

                # Construct the message
                message = f"Collection Score: {collection_score}\n" \
                    f"Fear and Greed Index: {fear_and_greed_index}\n" \
                    f"Market Dominance Score: {market_dominance_score}"
            else:
                message = "Failed to retrieve collection score or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."

        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)

    # Holder Trend

    elif data == "collection_holder":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            holder_data = await fetch_holder_data(contract_address)
            if holder_data and 'data' in holder_data and holder_data['data']:
                await plot_holder_trend(holder_data['data'][0], query.message)
            else:
                message = "Failed to retrieve holder data or no data available."
                await context.bot.send_message(chat_id=chat_id, text=message)
        else:
            message = "No contract address found. Please search for NFTs first."
            await context.bot.send_message(chat_id=chat_id, text=message)

        await nft_details_menu(update.callback_query.message, context)

    #Anomaly Detection
    elif data == "check_anomaly":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            score_data = get_collection_score(contract_address)
            if score_data and 'data' in score_data and score_data['data']:
                collection_data2 = score_data['data'][0]
                washtrade_index = collection_data2.get('washtrade_index', 'N/A')
                zero_profit_trades = collection_data2.get('zero_profit_trades', 'N/A')
                loss_making_volume = collection_data2.get('loss_making_volume', 'N/A')

                features = {
                    'washtrade_index': washtrade_index,
                    'zero_profit_trades': zero_profit_trades,
                    'loss_making_volume': loss_making_volume
                }
                prediction_result = await fetch_anomaly_prediction(features)
                message = f"Anomaly Prediction: {prediction_result.get('prediction', 'Unknown')}"
            else:
                message = "Failed to retrieve score data or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."
    
        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)

    #Price Predicition    
    elif data == "show_price":
        await query.message.reply_text("Please send the token ID for price prediction.")
        context.chat_data['action'] = 'awaiting_token_id'
    
    # MarketCap and Volume trend

    elif data=="mpc":
        await show_trend_options(update, context)

   
    elif data.startswith("trend_"):
        chat_id = query.message.chat_id
        time_range = data.split("_")[1]
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            trend_data = await market_price_trend.fetch_market_price_trends(contract_address, time_range)
            if trend_data and 'data' in trend_data and trend_data['data']:
                await market_price_trend.plot_trends(trend_data, query.message)
                message = "The trends have been displayed above."
            else:
                message = "Failed to retrieve trend data or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."

        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(query.message, context)

    # Washtrader Trend
    if data == "show_washtrade_options":
        await show_washtrade_trend_options(update.callback_query, context)
    elif (data.startswith("washtrade_") and data.count('_') == 2) or (data.startswith("washtrade_suspect_sales_") and data.count('_') == 3):  # Data format: washtrade_assets_trend
        trend_type = data 
        await show_washtrade_time_range_options(update.callback_query, context, trend_type)
    elif (((data.startswith("washtrade_assets_") or data.startswith("washtrade_volume_") or data.startswith("washtrade_wallets_")) and data.count('_') == 3) or (data.startswith("washtrade_suspect_sales_") and data.count('_') == 4)):  # Data format: washtrade_assets_trend_24h
        parts = data.split('_')
        if len(parts)==5:
            trend_type = "_".join(parts[0:4])
            time_range = parts[-1]
            await display_washtrade_trends(query.message, context.chat_data.get('nft_contract_address'), trend_type, time_range)
            
        else:
            trend_type = "_".join(parts[0:3])
            time_range = parts[-1]
            await display_washtrade_trends(query.message, context.chat_data.get('nft_contract_address'), trend_type, time_range)
        await nft_details_menu(query.message, context)

    # Analytics
    elif data == "show_analytics":
        await show_analytics_menu(update, context)
    elif data.startswith("analytics_"):
        time_range = data.split("_")[1]
        await fetch_and_display_analytics(update, context, time_range)

    # Traders Trend
    elif data=="trader_trend":
        await show_trader_trend_menu(update, context)

    elif data.startswith("trader_trend_"):
        _, _, time_range = data.split("_")
        await show_specific_trader_trend_menu(query.message, context, time_range)
    if data.startswith("traders_"):
        parts = data.split("_")
        if len(parts) == 4:
            trend_type = "_".join(parts[0:3])
            time_range = parts[3]
            await display_trader_trend(query.message, context.chat_data.get('nft_contract_address'), trend_type, time_range)
            await nft_details_menu(query.message, context)
        elif len(parts) == 3:
            trend_type = "_".join(parts[0:2])
            time_range = parts[2]
            await display_trader_trend(query.message, context.chat_data.get('nft_contract_address'), trend_type, time_range)
            await nft_details_menu(query.message, context)
        else:
            await query.message.reply_text("Unexpected trend format. Please try again.")
            await nft_details_menu(query.message, context)

    # Go Back
    elif data == "go_back":
        await display_options(query.message, context)

async def handle_message(update: Update, context: CallbackContext) -> None:
    action = context.chat_data.get('action')

    if action == 'awaiting_contract':
        contract_address = update.message.text
        context.chat_data['nft_contract_address'] = contract_address
        await nft_details_menu(update, context)
    elif action == 'awaiting_token_id':
        token_id = update.message.text
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            price_data = get_price_prediction(contract_address, token_id)
            if (price_data):
                message = f"Price Estimate: {price_data['price_estimate']}\n" \
                        f"Lower Bound: {price_data['price_estimate_lower_bound']}\n" \
                        f"Upper Bound: {price_data['price_estimate_upper_bound']}"
            else:
                message = "Token Id not found"
        else:
            message = "No contract address found. Please search for NFTs first."
        await update.message.reply_text(message)
        await nft_details_menu(update, context)
    else:
        await display_options(update, context)

def run_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    run_bot()
