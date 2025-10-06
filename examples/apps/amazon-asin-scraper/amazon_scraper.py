"""
Amazon.de ASIN Product Scraper

This web application scrapes product information from Amazon.de using ASIN numbers.
Supports single ASIN or multiple comma-separated ASINs.

Requirements:
- gradio (install with: uv pip install gradio)
- OpenAI API key (set in .env or as environment variable)

Usage:
    python amazon_scraper.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

import gradio as gr  # type: ignore
from pydantic import BaseModel, Field

from browser_use import Agent, ChatOpenAI
from browser_use.browser import BrowserSession


class AmazonProduct(BaseModel):
	"""Schema for Amazon product information."""

	asin: str = Field(description='Amazon Standard Identification Number')
	title: str = Field(description='Product title/name')
	price: str | None = Field(default=None, description='Product price with currency')
	rating: str | None = Field(default=None, description='Average customer rating')
	reviews_count: str | None = Field(default=None, description='Number of customer reviews')
	availability: str | None = Field(default=None, description='Stock availability status')
	brand: str | None = Field(default=None, description='Product brand/manufacturer')
	description: str | None = Field(default=None, description='Product description')
	features: list[str] | None = Field(default=None, description='Key product features/bullet points')
	images: list[str] | None = Field(default=None, description='Product image URLs')
	url: str = Field(description='Full Amazon.de product URL')


class AmazonProductList(BaseModel):
	"""Schema for multiple Amazon products."""

	products: list[AmazonProduct] = Field(description='List of scraped Amazon products')
	scraped_at: str = Field(description='Timestamp when data was scraped')


async def scrape_amazon_asin(
	asin_input: str,
	api_key: str,
	model: str = 'gpt-4.1-mini',
	headless: bool = True,
) -> str:
	"""
	Scrape Amazon.de product information for given ASIN(s).

	Args:
	    asin_input: Single ASIN or comma-separated ASINs
	    api_key: OpenAI API key
	    model: LLM model to use
	    headless: Run browser in headless mode

	Returns:
	    JSON string with product information
	"""
	if not api_key.strip():
		return json.dumps({'error': 'Please provide an OpenAI API key'}, indent=2)

	if not asin_input.strip():
		return json.dumps({'error': 'Please provide at least one ASIN'}, indent=2)

	# Parse ASINs from input
	asins = [asin.strip() for asin in asin_input.split(',') if asin.strip()]

	if not asins:
		return json.dumps({'error': 'No valid ASINs found in input'}, indent=2)

	# Set API key
	os.environ['OPENAI_API_KEY'] = api_key

	try:
		# Create browser session
		browser_session = BrowserSession(headless=headless)

		# Build URLs for each ASIN
		amazon_urls = [f'https://www.amazon.de/dp/{asin}' for asin in asins]

		# Create task for the agent
		if len(asins) == 1:
			task = f"""
Go to Amazon.de product page: {amazon_urls[0]}

Extract the following product information:
- ASIN: {asins[0]}
- Product title
- Price (with currency symbol)
- Customer rating (e.g., "4.5 out of 5 stars")
- Number of reviews
- Availability/stock status
- Brand/manufacturer
- Product description
- Key features/bullet points
- Product image URLs

Return the data in a structured format matching the AmazonProduct schema.
"""
		else:
			task = f"""
Visit the following Amazon.de product pages and extract information for each:

{chr(10).join(f'{i + 1}. {url} (ASIN: {asin})' for i, (url, asin) in enumerate(zip(amazon_urls, asins)))}

For each product, extract:
- ASIN
- Product title
- Price (with currency symbol)
- Customer rating
- Number of reviews
- Availability/stock status
- Brand/manufacturer
- Product description
- Key features/bullet points
- Product image URLs

Return the data for all products in a structured format matching the AmazonProductList schema.
"""

		# Create agent with structured output
		llm = ChatOpenAI(model=model)

		if len(asins) == 1:
			output_schema = AmazonProduct
		else:
			output_schema = AmazonProductList

		agent = Agent(
			task=task,
			llm=llm,
			browser_session=browser_session,
			output_model_schema=output_schema,
			max_actions_per_step=3,
		)

		# Run agent and get structured output
		history = await agent.run()
		result = history.final_result()

		# Close browser session
		await browser_session.kill()

		if result:
			# Parse and validate the result
			try:
				if len(asins) == 1:
					product = AmazonProduct.model_validate_json(result)
					return product.model_dump_json(indent=2)
				else:
					product_list = AmazonProductList.model_validate_json(result)
					return product_list.model_dump_json(indent=2)
			except Exception as e:
				# Return raw result if validation fails
				return json.dumps(
					{
						'warning': f'Validation failed: {str(e)}',
						'raw_result': result,
					},
					indent=2,
				)
		else:
			return json.dumps({'error': 'No result returned from agent'}, indent=2)

	except Exception as e:
		return json.dumps({'error': f'Error during scraping: {str(e)}'}, indent=2)


def create_ui():
	"""Create Gradio web interface."""
	with gr.Blocks(
		title='Amazon.de ASIN Scraper',
		theme=gr.themes.Soft(),
	) as interface:
		gr.Markdown(
			"""
# 🛍️ Amazon.de ASIN Product Scraper

Scrape product information from Amazon.de using ASIN numbers.

**Features:**
- ✅ Single or multiple ASIN support (comma-separated)
- ✅ Structured JSON output
- ✅ Extracts: title, price, rating, reviews, availability, brand, description, features, images
- ✅ Uses AI to intelligently extract product data
"""
		)

		with gr.Row():
			with gr.Column(scale=1):
				gr.Markdown('### Input')

				api_key = gr.Textbox(
					label='OpenAI API Key',
					placeholder='sk-...',
					type='password',
					info='Your OpenAI API key for the LLM',
				)

				asin_input = gr.Textbox(
					label='ASIN Number(s)',
					placeholder='B08N5WRWNW or B08N5WRWNW, B09G9FPHY6, B0C1H26C46',
					lines=2,
					info='Enter single ASIN or comma-separated ASINs',
				)

				with gr.Row():
					model = gr.Dropdown(
						choices=['gpt-4.1-mini', 'gpt-4.1', 'gpt-5-mini'],
						label='Model',
						value='gpt-4.1-mini',
						info='LLM model to use',
					)

					headless = gr.Checkbox(
						label='Headless Mode',
						value=True,
						info='Run browser in background',
					)

				submit_btn = gr.Button('🔍 Scrape Products', variant='primary', size='lg')

				gr.Markdown(
					"""
### Examples:
- Single ASIN: `B08N5WRWNW`
- Multiple ASINs: `B08N5WRWNW, B09G9FPHY6, B0C1H26C46`
"""
				)

			with gr.Column(scale=1):
				gr.Markdown('### Output (JSON)')

				output = gr.Textbox(
					label='Product Information',
					lines=20,
					interactive=False,
					show_copy_button=True,
					placeholder='Product information will appear here in JSON format...',
				)

				gr.Markdown(
					"""
**Note:** Scraping may take 30-60 seconds per product depending on complexity.
The output will be formatted as JSON for easy integration with other tools.
"""
				)

		submit_btn.click(
			fn=lambda *args: asyncio.run(scrape_amazon_asin(*args)),
			inputs=[asin_input, api_key, model, headless],
			outputs=output,
		)

	return interface


if __name__ == '__main__':
	print('🚀 Starting Amazon.de ASIN Scraper...')
	print('📝 Make sure to set your OPENAI_API_KEY in .env or provide it in the web interface')
	print('🌐 Opening web interface...\n')

	demo = create_ui()
	demo.launch(
		server_name='0.0.0.0',
		server_port=7860,
		share=False,
	)
